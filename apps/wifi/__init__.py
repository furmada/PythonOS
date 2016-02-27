import pyos

try:
    import wifi
    functional = True
except:
    functional = False
    
def onStart(s, a):
    global state, app, fiapp
    state = s
    app = a
    fiapp = WifiApp()
    
class Network(pyos.GUI.Container):
    def __init__(self, cell):
        self.cell = cell
        super(Network, self).__init__((0, 0), color=state.getColorPalette().getColor("background"), width=fiapp.scroller.width, height=40,
                                      border=2, borderColor=(20, 20, 20))
        self.addChild(pyos.GUI.Image((0, 0), surface=state.getIcons().getLoadedIcon("info"), width=40, height=40, border=1, borderColor=(200, 200, 200),
                                     onClick=self.displayInfoDialog))
        self.addChild(pyos.GUI.Text((42, 4), str(self.cell.ssid), state.getColorPalette().getColor("item"), 24))
        self.connBtn = pyos.GUI.Button((self.width-50, 0), "Connected" if fiapp.currentCell==self.cell else "Connect",
                                       (100, 100, 200) if fiapp.currentCell==self.cell else (100, 200, 100), (20, 20, 20), 16,
                                       onClick=self.connectAsk, width=50, height=40)
        self.addChild(self.connBtn)
        
    def refresh(self):
        self.connBtn.setText("Connected" if fiapp.currentCell==self.cell else "Connect")
        self.connBtn.backgroundColor = (100, 100, 200) if fiapp.currentCell==self.cell else (100, 200, 100)
        super(Network, self).refresh()
        
    def connectAsk(self):
        if self.cell == fiapp.currentCell: return
        if self.cell.encrypted:
            pyos.GUI.AskDialog("Password", "The network "+str(self.cell.ssid)+" is encrypted using "+self.cell.encryption_type+". Enter the password.", self.connect).display()
        else:
            self.connect(None)
        
    def connect(self, pwd):
        try:
            try:
                scheme = wifi.Scheme.find("wlan0", self.cell.ssid)
                scheme.activate()
            except:
                scheme = wifi.Scheme.for_cell("wlan0", self.cell.ssid, self.cell, pwd)
                scheme.save()
                scheme.activate()
            state.getNotificationQueue().push(pyos.Notification("Connected", "Wifi: "+str(self.cell.ssid), image=state.getIcons().getLoadedIcon("wifi"),
                                                                source=app))
            fiapp.currentCell = self.cell
            app.parameters["network"] = self.cell
            self.refresh()
        except:
            pyos.GUI.OKDialog(str(self.cell.ssid), "Unable to connect to "+str(self.cell.ssid)).display()
        
    def displayInfoDialog(self):
        info = "Wireless Information\n"
        info += "SSID: "+str(self.cell.ssid)+"\n"
        info += "Security: "+(self.cell.encryption_type if self.cell.encrypted else "None")+"\n"
        info += "Signal strength: "+str(self.cell.signal)
        pyos.GUI.OKDialog(str(self.cell.ssid), info).display()
    
class WifiApp(object):
    def __init__(self):
        if not functional:
            pyos.GUI.ErrorDialog("The \"wifi\" module cannot be found on your system! pip install wifi.").display()
            return
        self.currentCell = app.parameters.get("network", None)
        self.scroller = pyos.GUI.ListPagedContainer((0, 40), width=app.ui.width, height=app.ui.height-40,
                                                         color=state.getColorPalette().getColor("background"), margin=0)
        self.titleText = pyos.GUI.Text((2, 4), "WiFi Networks", state.getColorPalette().getColor("item"), 24)
        self.refreshBtn = pyos.GUI.Button((app.ui.width-80, 0), "Refresh", (100, 200, 100), (20, 20, 20), 18, width=80, height=40,
                                          onClick=self.populate)
        app.ui.addChild(self.titleText)
        app.ui.addChild(self.refreshBtn)
        app.ui.addChild(self.scroller)
        self.populate()
        
    def populate(self):
        try:
            self.scroller.clearChildren()
            for net in wifi.Cell.all("wlan0"):
                self.scroller.addChild(Network(net))
        except:
            pyos.GUI.ErrorDialog("Unable to scan for networks.").display()
        