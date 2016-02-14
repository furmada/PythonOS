import pyos
import os

mounted = []

def onStart(s, a):
    global state, app, mounter
    state = s
    app = a
    mounter = USBMount()
    
class USBEntry(pyos.GUI.Container):
    def __init__(self, device, **data):
        data["onClickData"] = (self,)
        super(USBEntry, self).__init__((0, 0), **data)
        self.SKIP_CHILD_CHECK = True
        self.device = device
        self.location = None
        self.mounted = device in mounted
        self.title = None
        if self.mounted:
            self.title = pyos.GUI.Text((2, 8), self.device.strip("/dev/"), (100, 200, 100), 24)
        else:
            self.title = pyos.GUI.Text((2, 8), self.device.strip("/dev/"), state.getColorPalette().getColor("item"), 24)
        self.addChild(self.title)
        
    def recheck(self):
        self.clearChildren()
        if self.mounted:
            self.title = pyos.GUI.Text((2, 8), self.device.strip("/dev/"), (100, 200, 100), 24)
        else:
            self.title = pyos.GUI.Text((2, 8), self.device.strip("/dev/"), state.getColorPalette().getColor("item"), 24)
        self.addChild(self.title)
    
class USBMount(object):
    def __init__(self):
        self.usblist = pyos.GUI.ListScrollableContainer((0, 40), width=app.ui.width, height=app.ui.height-40, scrollAmount=40, color=state.getColorPalette().getColor("background"))
        app.ui.addChild(pyos.GUI.Text((2, 8), "USB List", state.getColorPalette().getColor("item"), 24))
        app.ui.addChild(pyos.GUI.Button((app.ui.width-80, 0), "Refresh", (100, 200, 100), (20, 20, 20), 24, onClick=self.refresh))
        app.ui.addChild(self.usblist)
        self.populateList()
        
    def mountAsk(self, dev):
        pyos.GUI.OKCancelDialog("Mount", "Please select a folder to mount "+dev.device+" in.", self.mountSelect, (dev,)).display()
        
    def mountSelect(self, dev, resp):
        if resp == "OK":
            state.getApplicationList().getApp("files").getModule().FolderPicker((10, 10), width=app.ui.width-20, height=app.ui.height-20,
                                                                                onSelect=self.mount, onSelectData=(dev,)).display()
        
    def mount(self, device, loc):
        global mounted
        mounted.append(device.device)
        device.location = os.path.join(loc, "USB"+str(len(mounted)+1))
        os.mkdir(device.location)
        os.system("sudo mount -t auto "+device.device+" "+device.location)
        self.populateList()
        
    def unmountAsk(self, dev):
        pyos.GUI.YNDialog("Unmount", "Are you sure you want to unmount "+dev.device+"?", self.unmount, (dev,)).display()
        
    def unmount(self, device, resp):
        global mounted
        if resp == "Yes":
            mounted.remove(device.device)
            os.system("sudo umount "+device.location)
            os.rmdir(device.location)
            self.populateList()
            
    def doProperAction(self, device):
        if device.mounted:
            unmountAsk(device)
        else:
            mountAsk(device)
        
    def populateList(self):
        self.usblist.clearChildren()
        for dev in self.getList():
            self.usblist.addChild(USBEntry(dev, width=self.usblist.container.width, height=40, color=state.getColorPalette().getColor("background"),
                                           onClick=self.doProperAction))
        
    def getList(self):
        try:
            return [os.path.join("/dev/", device) for device in os.listdir("/dev/") if (device.find("sd") != -1 and len(device) > 3)]
        except:
            pyos.GUI.ErrorDialog("Unable to list /dev/.").display()
            return []
    
    def refresh(self):
        for child in self.usblist.container.childComponents:
            child.recheck()
        if len(self.usblist.container.childComponents) == 0:
            self.populateList()
    