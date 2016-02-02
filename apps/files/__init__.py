import pyos
from shutil import move, copy2, copytree
from sys import platform

application = None
state = None

navigator = None 

pathIndicator = None
fileOpeners = {}
selected = []

pathText = None
container = None

picker = None
    
def loadFileOpeners():
    global fileOpeners
    fileOpeners = {}
    for app in state.getApplicationList().applications.values():
        if "file" in app.parameters:
            print "registered file-opener app "+app.name
            fileOpeners[app] = {
                                  "method": getattr(app.module, app.parameters["file"]["method"]),
                                  "supported": app.parameters["file"]["supported"],
                                  "startFirst": app.parameters["file"].get("startFirst", app.thread.firstRun)
                                  }
            
def getAppsForFileType(ftype):
    apps = []
    for app in fileOpeners.keys():
        if ftype in fileOpeners[app]["supported"]:
            apps.append([app.title, fileOpeners[app]["method"], fileOpeners[app]["startFirst"], app])
    return apps

def appSelDialog(path, short):
    apps = getAppsForFileType(navigator.getExtension(short))
    if len(apps) == 0:
        pyos.GUI.OKDialog("Unsupported", "The file "+short+" cannot be opened because no installed app supports its format.").display()
        return
    if len(apps) == 1:
        if apps[0][2]:
            apps[0][3].onStart()
        apps[0][3].activate(noOnStart=True)
        apps[0][1](state, apps[0][3], path)
        return
    selector = pyos.GUI.Selector((0, 0), [app[0] for app in apps], width=state.getGUI().width, height=40,
                                 onValueChanged=startAppForPath, onValueChangedData=(apps,path))
    selector.overlay.display()
    
def startAppForPath(entries, path, title):
    entry = None
    for e in entries:
        if e[0] == title:
            entry = e
            break
    if entry == None: return
    if entry[2]:
        entry[3].onStart()
    entry[3].activate(noOnStart=True)
    entry[1](state, entry[3], path)

def goToPath():
    dialog = pyos.GUI.AskDialog("Location", "Enter the path of the location you want to navigate to.", navigator.toAbs)
    dialog.display()
    
def passSelectedDir(to, overlay):
    if len(selected) == 0:
        to([navigator.path])
        overlay.hide()
        return
    to(selected)
    overlay.hide()
    
class Operations:
    @staticmethod
    def delete():
        global selected
        for path in selected:
            if pyos.os.path.isfile(path):
                pyos.os.remove(path)
            if pyos.os.path.isdir(path):
                pyos.rmtree(path, True)
            selected.remove(path)
    
    @staticmethod            
    def move():
        global selected
        for path in selected:
            if pyos.os.path.isfile(path):
                move(path.rstrip("\\").rstrip("/"), navigator.path)
            if pyos.os.path.isdir(path):
                move(path, navigator.path)
            selected.remove(path)
            
    @staticmethod
    def copy():
        global selected
        for path in selected:
            if pyos.os.path.isfile(path):
                copy2(path.rstrip("\\").rstrip("/"), navigator.path)
            if pyos.os.path.isdir(path):
                copytree(path, navigator.path)
            selected.remove(path)
            
class Navigator(object):
    def __init__(self):
        self.path = str(pyos.__file__).rstrip("pyos.py").rstrip("pyos.pyc")
        if platform == "win32":
            self.slash = "\\"
        else:
            self.slash = "/"
        
    def up(self):
        self.path = self.path.rstrip(self.slash)[:self.path.rstrip(self.slash).rfind(self.slash)+1]
        load()
        
    def home(self):
        self.path = str(pyos.__file__).rstrip("pyos.py").rstrip("pyos.pyc")
        load()
        
    def toSub(self, sub, selMode=False):
        combined = pyos.os.path.join(self.path, sub)
        if pyos.os.path.isfile(combined):
            if selMode:
                picker.select(combined)
                return
            appSelDialog(combined, sub)
        else:
            if pyos.os.path.isdir(combined):
                self.path = combined
                load()
                
    def toAbs(self, path):
        if path == "Cancel": return
        self.path = path
        load()
        
    def subToAbs(self, path):
        return pyos.os.path.join(self.path, path)
    
    def contFolder(self, path):
        return path.rstrip(self.slash)[:path.rstrip(self.slash).rfind(self.slash)+1]
    
    def getExtension(self, path):
        return path[path.rfind("."):]

def getDefaultButtonBar():
    buttonBar = pyos.GUI.ButtonRow((0, 0), width=application.ui.width, height=40, color=state.getColorPalette().getColor("background"), padding=0, margin=0,
                                   border=1, borderColor=state.getColorPalette().getColor("accent"))
    button_home = pyos.GUI.Image((0,0), path="res/icons/files_home.png", width=40, height=40,
                                 onClick=navigator.home)
    button_up = pyos.GUI.Image((0,0), path="res/icons/files_up.png", width=40, height=40,
                                 onClick=navigator.up)
    button_goto = pyos.GUI.Image((0,0), path="res/icons/files_goto.png", width=40, height=40,
                                 onClick=goToPath)
    button_delete = pyos.GUI.Image((0,0), path="res/icons/files_delete.png", width=40, height=40,
                                 onClick=Operations.delete)
    button_move = pyos.GUI.Image((0,0), path="res/icons/files_move.png", width=40, height=40,
                                 onClick=Operations.move)
    button_copy = pyos.GUI.Image((0,0), path="res/icons/files_copy.png", width=40, height=40,
                                 onClick=Operations.copy)
    buttonBar.addChild(button_home)
    buttonBar.addChild(button_up)
    buttonBar.addChild(button_goto)
    buttonBar.addChild(button_delete)
    buttonBar.addChild(button_move)
    buttonBar.addChild(button_copy)
    return buttonBar

def getSelectButtonBar():
    buttonBar = pyos.GUI.ButtonRow((0, 0), width=application.ui.width, height=40, color=state.getColorPalette().getColor("background"), padding=0, margin=0,
                                   border=1, borderColor=state.getColorPalette().getColor("accent"))
    button_select = pyos.GUI.Image((0,0), path="res/icons/files_select.png", width=40, height=40,
                                 onClick=picker.select, onClickData=("current",))
    button_home = pyos.GUI.Image((0,0), path="res/icons/files_home.png", width=40, height=40,
                                 onClick=navigator.home)
    button_up = pyos.GUI.Image((0,0), path="res/icons/files_up.png", width=40, height=40,
                                 onClick=navigator.up)
    button_goto = pyos.GUI.Image((0,0), path="res/icons/files_goto.png", width=40, height=40,
                                 onClick=goToPath)
    buttonBar.addChild(button_select)
    buttonBar.addChild(button_home)
    buttonBar.addChild(button_up)
    buttonBar.addChild(button_goto)
    return buttonBar

def select(cont, path):
    selected.append(navigator.subToAbs(path))
    cont.backgroundColor = state.getColorPalette().getColor("accent")

def deselect(cont, path):
    selected.remove(navigator.subToAbs(path))
    if cont != None:
        cont.backgroundColor = state.getColorPalette().getColor("background")
        
def toggleSelect(cont, path):
    if cont.backgroundColor == state.getColorPalette().getColor("accent"):
        deselect(cont, path)
    else:
        select(cont, path)
        
def fileInfoDialog(path, short):
    isFile = pyos.os.path.isfile(path)
    infostr = "Resource information for "+short+"\n\n"
    if isFile:
        infostr += "Size: "+str(pyos.os.path.getsize(path) / 1000)+"kb\n"
    else:
        infostr += "Directory Children: "+str(len(pyos.os.listdir(path)))+"\n"
    pyos.GUI.OKDialog(short, infostr).display()

def getFileEntry(fpath, selMode=False):
    if fpath.startswith("."): return False
    abspath = navigator.subToAbs(fpath)
    cont = pyos.GUI.Container((0, 0), width=container.container.width, height=30, color=state.getColorPalette().getColor("background"),
                              onClick=navigator.toSub, onClickData=(fpath, selMode))
    isFile = pyos.os.path.isfile(abspath)
    icon = None
    if isFile:
        icon = pyos.GUI.Image((0, 0), path="res/icons/file.png", width=30, height=30,
                              onClick=toggleSelect, onClickData=(cont, fpath))
    else:
        icon = pyos.GUI.Image((0, 0), path="res/icons/folder.png", width=30, height=30,
                              onClick=toggleSelect, onClickData=(cont, fpath))
    filename = pyos.GUI.Text((32, 7), fpath, state.getColorPalette().getColor("item"), 15,
                             onClick=navigator.toSub, onClickData=(fpath, selMode))
    size = None
    if isFile:
        size = pyos.GUI.Text((cont.width-35, 7), str(pyos.os.path.getsize(fpath) / 1000)+"kb", state.getColorPalette().getColor("item"), 15,
                             onClick=fileInfoDialog, onClickData=(abspath, fpath))
    else:
        size = pyos.GUI.Text((cont.width-35, 7), "dir", state.getColorPalette().getColor("item"), 15,
                             onClick=fileInfoDialog, onClickData=(abspath, fpath))
    cont.addChild(icon)
    cont.addChild(filename)
    cont.addChild(size)
    if abspath in selected:
        cont.backgroundColor = state.getColorPalette().getColor("accent")
    cont.refresh()
    return cont

def load(selMode=False):
    pathText.text = navigator.path
    pathText.refresh()
    try:
        container.clearChildren()
    except: pass
    for loc in sorted([p for p in pyos.os.listdir(navigator.path) if pyos.os.path.isdir(p)]) + sorted([p for p in pyos.os.listdir(navigator.path) if pyos.os.path.isfile(p)]):
        entry = getFileEntry(loc)
        if entry:
            container.addChild(entry)
    #container.goToPage()
    
def loadUI():
    global container, pathText, navigator
    loadFileOpeners()
    navigator = Navigator()
    container = pyos.GUI.ListScrollableContainer((0,50), width=application.ui.width, height=application.ui.height-50, padding=0, margin=0)
    pathText = pyos.GUI.Text((0, 40), navigator.path, state.getColorPalette().getColor("item"), 10, width=application.ui.width)
    bar = getDefaultButtonBar()
    application.ui.addChild(bar)
    application.ui.addChild(pathText)
    application.ui.addChild(container)
    load()

def onStart(s, a):
    global application, state
    application = a
    state = s
    loadUI()
    
class LocationPicker(pyos.GUI.Overlay):
    def __init__(self, onSelected, accept="files"):
        global application, state, container, pathText, navigator, picker
        picker = self
        self.accept = accept
        self.onSelected = onSelected
        self.application = state.getActiveApplication()
        application = self.application
        super(LocationPicker, self).__init__((0, 0), width=self.application.ui.width, height=self.application.ui.height)
        loadFileOpeners()
        navigator = Navigator()
        container = pyos.GUI.ListScrollableContainer((0,50), width=application.ui.width, height=application.ui.height-50, padding=0, margin=0)
        pathText = pyos.GUI.Text((0, 40), navigator.path, state.getColorPalette().getColor("item"), 10, width=application.ui.width)
        bar = getSelectButtonBar()
        self.baseContainer.addChild(bar)
        self.baseContainer.addChild(pathText)
        self.baseContainer.addChild(container)
        load()
        
    def hide(self):
        global picker
        picker = None
        super(LocationPicker, self).hide()
        
    def select(self, path):
        if path == "current": path = navigator.path
        if self.accept == "file" and pyos.os.path.isfile(path):
            self.hide()
            passSelectedDir(self.onSelected, self)
            return
        else:
            pyos.GUI.OKDialog("Invalid File", "The application requested a file, but you selected a directory. Select a file instead.").display()
            return
        if self.accept == "folder" and pyos.os.path.isdir(path):
            self.hide()
            passSelectedDir(self.onSelected, self)
        else:
            pyos.GUI.OKDialog("Invalid Folder", "The application requested a directory, but you selected a file. Select a folder instead.").display()