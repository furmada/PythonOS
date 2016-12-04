import pyos

def onStart(s, a):
    global state, app, hub
    state = s
    app = a
    hub = Hub()
    MainScreen().activate()
    
def readJSON(path):
    try:
        f = open(path, "rU")
        jsd = pyos.json.loads(str(unicode(f.read(), errors="ignore")))
        f.close()
        return jsd
    except:
        return {}
    
class Screen(pyos.GUI.Container):
    def __init__(self, name):
        self.name = name
        super(Screen, self).__init__((0, 0), width=app.ui.width, height=app.ui.height)
        
    def activate(self):
        if self not in hub.screens:
            hub.openScreen(self)
            return
        self.oldtitle = state.getFunctionBar().app_title_text.text
        state.getFunctionBar().app_title_text.setText(self.name)
        app.ui.clearChildren()
        app.ui.addChild(self)
    
    def deactivate(self):
        state.getFunctionBar().app_title_text.setText(self.oldtitle)
        
class ManifestEditScreen(Screen):
    def __init__(self, title, appn):
        super(ManifestEditScreen, self).__init__(title)
        self.app = appn
        self.refresh()
        
    def genEntry(self, entry):
        cont = pyos.GUI.Container((0, 0), width=self.scroller.container.width, height=40, border=1)
        txt = pyos.GUI.Text((0, 13), entry+": ")
        cont.addChild(txt)
        cont.tef = pyos.GUI.TextEntryField((txt.width+5, 8), self.entries[entry], width=cont.width-txt.width-5, height=24)
        cont.entry = entry
        cont.addChild(cont.tef)
        return cont
        
    def refresh(self):
        self.data = readJSON(pyos.os.path.join("apps", self.app, "app.json")) if pyos.os.path.exists(pyos.os.path.join("apps", self.app, "app.json")) else {}
        self.entries = {
                        "name": self.data.get("name", self.app),
                        "title": self.data.get("title", ""),
                        "version": str(self.data.get("version", 1.0)),
                        "author": self.data.get("author", ""),
                        "description": self.data.get("description", ""),
                        "icon": self.data.get("more", {}).get("icon", ""),
                        "colorScheme": self.data.get("more", {}).get("colorScheme", "normal"),
                        "onStart": self.data.get("more", {}).get("onStart", ""),
                        "onStop": self.data.get("more", {}).get("onStop", ""),
                        "onPause": self.data.get("more", {}).get("onPause", ""),
                        "onResume": self.data.get("more", {}).get("onResume", ""),
                        }
        self.clearChildren()
        self.scroller = pyos.GUI.ListScrollableContainer((0, 0), width="100%", height=self.height-40, scrollAmount=40)
        for le in self.entries.iterkeys():
            self.scroller.addChild(self.genEntry(le))
        self.addChild(self.scroller)
        self.addChild(pyos.GUI.Image((0, self.height-40), surface=state.getIcons().getLoadedIcon("back"),
                                     onClick=self.close))
        self.addChild(pyos.GUI.Button((40, self.height-40), "Open in Editor", (43, 23, 122), width=self.width-40, height=40,
                                      onClick=self.openEditor))
        
    def collectData(self):
        for cont in self.scroller.container.childComponents:
            self.entries[cont.entry] = cont.tef.getText()
        
    def save(self):
        self.collectData()
        if self.data.get("more", None) == None:
            self.data["more"] = {}
        self.data["name"] = self.entries["name"]
        if self.entries["title"] != "": self.data["title"] = self.entries["title"]
        else: self.entries["title"] = self.entries["name"]
        self.data["version"] = float(self.entries["version"])
        if self.entries["author"] != "": self.data["author"] = self.entries["author"]
        if self.entries["description"] != "":self.data["description"] = self.entries["description"]
        if self.entries["icon"] != "": self.data["more"]["icon"] = self.entries["icon"]
        self.data["more"]["colorScheme"] = self.entries["colorScheme"]
        if self.entries["onStart"] != "": self.data["more"]["onStart"] = self.entries["onStart"] 
        if self.entries["onStop"] != "": self.data["more"]["onStop"] = self.entries["onStop"]
        if self.entries["onPause"] != "": self.data["more"]["onPause"] = self.entries["onPause"]
        if self.entries["onResume"] != "": self.data["more"]["onResume"] = self.entries["onResume"]
        f = open(pyos.os.path.join("apps", self.app, "app.json"), "w")
        pyos.json.dump(self.data, f)
        f.close()
        
    def close(self):
        self.save()
        hub.closeLast()
        
    def openEditor(self):
        self.save()
        state.getApplicationList().getApp("editor").file = pyos.os.path.join("apps", self.app, "app.json")
        state.getApplicationList().getApp("editor").activate()
        hub.closeLast()
        
class MainScreen(Screen):
    def __init__(self):
        super(MainScreen, self).__init__("Developer Hub")
        self.refresh()
        
    def refresh(self):
        self.clearChildren()
        self.apps = app.dataStore.get("apps", [])
        self.checkApps()
        self.app = app.dataStore.get("currentApp", None)
        sac = self.apps[:]
        if self.app != None:
            sac.remove(self.app)
            sac.insert(0, self.app)
        self.appsel = pyos.GUI.Selector((0, 0), sac+["+ Add App"], width="80%", height="20%",
                                        color=state.getColorPalette().getColor("item"),
                                        textColor=state.getColorPalette().getColor("background"), onValueChanged=self.selectApp)
        self.addChild(self.appsel)
        wd = self.width-self.appsel.width
        self.addChild(pyos.GUI.Image(("80%", 0), surface=state.getIcons().getLoadedIcon("delete"), width=wd, height=self.appsel.height,
                                     onClick=self.removeAppAsk))
        self.addChild(pyos.GUI.Button((0, "20%"), "View Last Error", (150, 50, 50), width="100%", height="20%",
                                      onClick=self.viewError))
        if self.app != None:
            self.addChild(pyos.GUI.Button((0, "40%"), "Edit Manifest", (43, 23, 122), width="100%", height="20%",
                                          onClick=self.openManifest))
            if self.app not in state.getApplicationList().applications.keys():
                self.addChild(pyos.GUI.Button((0, "60%"), "Add to System", (163, 132, 88), width="100%", height="20%",
                                              onClick=self.addToSystemAsk))
            else:
                self.addChild(pyos.GUI.Button((0, "60%"), "Launch", (50, 150, 50), width="100%", height="20%",
                                              onClick=self.launch))
            self.addChild(pyos.GUI.Button((0, "80%"), "Create Package", (133, 72, 23), width="100%", height="20%",
                                          onClick=self.packageAsk))
            
    def checkApps(self):
        for a in self.apps:
            if not pyos.os.path.exists(pyos.os.path.join("apps", a)):
                self.app = a
                self.removeApp("Yes")
            
    def openManifest(self):
        ManifestEditScreen(self.app+" Manifest", self.app).activate()
            
    def addAppAsk(self):
        pyos.GUI.Dialog("Add App", "Do you want to add an app with an existing folder or create a new one?", ["New", "Existing", "Cancel"],
                        self.addAppParse).display()    
        
    def addAppParse(self, resp):
        if resp == "New":
            self.addAppNameAsk()
        if resp == "Existing":
            pyos.GUI.OKDialog("Add App", "Select the app's folder.",
                              self.addAppParse).display()
        if resp == "OK":
            state.getApplicationList().getApp("files").getModule().FolderPicker(("2%", "2%"), width="96%", height="96%",
                                                                                startFolder="apps/", onSelect=self.addApp).display()
        
    def addAppNameAsk(self): 
        pyos.GUI.AskDialog("App Name", "Enter the name of the new app. A folder will be created under apps/",
                           self.addApp).display()   
                           
    def addApp(self, appn):
        if appn == "Cancel": return
        if pyos.os.path.exists(appn):
            appn = appn.replace("\\", "/").lstrip("apps/")
        else:
            try:
                pyos.os.mkdir(pyos.os.path.join("apps", appn))
            except:
                pyos.GUI.WarningDialog("Failed to create the app folder. It may already exist.").display()
        try:
            if not pyos.os.path.exists(pyos.os.path.join("apps", appn, "__init__.py")):
                f = open(pyos.os.path.join("apps", appn, "__init__.py"), "w")
                f.write("\"\"\"Python OS 6 Package *autocreated*\"\"\"\nimport pyos\n\n")
                f.close()
        except:
            pass
        self.apps.append(appn)
        app.dataStore["apps"] = self.apps
        self.selectApp(appn)
        
    def removeAppAsk(self):
        pyos.GUI.YNDialog("Remove App", "Are you sure you want to remove the app "+self.app+" from the Hub? Its data will not be removed.",
                          self.removeApp).display()
                          
    def removeApp(self, resp):
        if resp == "Yes":
            self.apps.remove(self.app)
            app.dataStore["apps"] = self.apps
            self.app = self.apps[len(self.apps)-1] if len(self.apps) > 0 else None
            app.dataStore["currentApp"] = self.app
            hub.refresh()
        
    def selectApp(self, name):
        if name != "+ Add App":
            self.app = name
            app.dataStore["currentApp"] = self.app
            hub.refresh()
        else:
            self.addAppAsk()
            
    def viewError(self):
        if pyos.os.path.exists("temp/last_error.txt"):
            state.getApplicationList().getApp("file-reader").file = "temp/last_error.txt"
            state.getApplicationList().getApp("file-reader").activate()
        else:
            pyos.GUI.WarningDialog("The file \"temp/last_error.txt\" does not exist.").display()
            
    def launch(self):
        state.getApplicationList().getApp(self.app).activate()
        
    def addToSystemAsk(self):
        pyos.GUI.OKCancelDialog("Register App", "The application "+self.app+" will be added to the system and will appear in the Launcher.",
                                self.addToSystem).display()
        
    def addToSystem(self, resp):
        if resp == "OK":
            try:
                pyos.Application.registerDebugApp(pyos.os.path.join("apps", self.app))
            except:
                pyos.GUI.ErrorDialog("The app "+self.app+" could not be added! Ensure it has a proper manifest.").display()
                
    def packageAsk(self):
        pyos.GUI.OKCancelDialog("Package App", "The application "+self.app+" will be packaged. Select the destination folder.",
                                self.packageParse).display()
        
    def packageParse(self, resp):
        if resp == "Cancel": return
        state.getApplicationList().getApp("files").getModule().SaveAs("Enter the package name. This should be the app's name",
                                                                      extension=".zip", onSelect=self.package).display()
                
    def package(self, path):
        state.getGUI().displayStandbyText("Creating "+path)
        zf = pyos.ZipFile(path, "w")
        for itm in pyos.os.listdir(pyos.os.path.join("apps", self.app)):
            zf.write(pyos.os.path.join("apps", self.app, itm), itm)
        zf.close()
        pyos.GUI.OKDialog("Package Created", "The app "+self.app+" has been packaged to "+path).display()
    
class Hub(object):
    def __init__(self):
        self.screens = []
        
    def refresh(self):
        self.screens[len(self.screens)-1].refresh()
        
    def openScreen(self, s):
        self.screens.append(s)
        s.activate()
        
    def closeLast(self):
        self.screens.pop().deactivate()
        self.screens[len(self.screens)-1].activate()