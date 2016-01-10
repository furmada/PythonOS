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
        apps[0][3].activate()
        apps[0][1](path)
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
    entry[3].activate()
    entry[1](path)

def goToPath():
    dialog = pyos.GUI.AskDialog("Location", "Enter the path of the location you want to navigate to.", navigator.toAbs)
    dialog.display()
    
def passSelectedDir(to):
    to(navigator.path)
    
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
        
    def toSub(self, sub):
        combined = pyos.os.path.join(self.path, sub)
        if pyos.os.path.isfile(combined):
            appSelDialog(combined, sub)
        else:
            if pyos.os.path.isdir(combined):
                self.path = combined
                load()
                
    def toAbs(self, path):
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

def getSelectButtonBar(passTo):
    buttonBar = pyos.GUI.ButtonRow((0, 0), width=application.ui.width, height=40, color=state.getColorPalette().getColor("background"), padding=0, margin=0,
                                   border=1, borderColor=state.getColorPalette().getColor("accent"))
    button_select = pyos.GUI.Image((0,0), path="res/icons/files_select.png", width=40, height=40,
                                 onClick=passSelectedDir, onClickData=(passTo,))
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

def getFileEntry(path):
    if path.startswith("."): return False
    abspath = navigator.subToAbs(path)
    cont = pyos.GUI.Container((0,0), width=application.ui.width, height=30, color=state.getColorPalette().getColor("background"), fullPath=abspath,
                              onClick=navigator.toSub, onClickData=(path,))
    if abspath in selected:
        cont.backgroundColor = state.getColorPalette().getColor("accent")
    icon = None
    if pyos.os.path.isfile(abspath):
        icon = pyos.GUI.Image((0,0), path="res/icons/file.png", width=30, height=30,
                              onClick=toggleSelect, onClickData=(cont, path))
    elif pyos.os.path.isdir(abspath):
        icon = pyos.GUI.Image((0,0), path="res/icons/folder.png", width=30, height=30,
                          onClick=toggleSelect, onClickData=(cont, path))
    else:
        return False
    text = pyos.GUI.Text((35, 7), path, state.getColorPalette().getColor("item"), 15,
                         onClick=navigator.toSub, onClickData=(path,))
    sizeText = "-"
    if pyos.os.path.isfile(abspath):
        try:
            sizeText = str(pyos.os.path.getsize(abspath) / 1000)+"kb"
        except:
            sizeText = "0kb"
    elif pyos.os.path.isdir(abspath):
        sizeText = "dir"
    size = pyos.GUI.Text((application.ui.width-35, 7), sizeText, state.getColorPalette().getColor("item"), 15)
    cont.addChild(icon)
    cont.addChild(text)
    cont.addChild(size)
    return cont

def load():
    pathText.text = navigator.path
    pathText.refresh()
    try:
        container.clearChildren()
    except: pass
    for loc in pyos.os.listdir(navigator.path):
        entry = getFileEntry(loc)
        if entry:
            container.addChild(entry)
    container.goToPage()

def onStart(s, a):
    global application, state, container, pathText, navigator
    application = a
    state = s
    loadFileOpeners()
    navigator = Navigator()
    container = pyos.GUI.ListPagedContainer((0,50), width=application.ui.width, height=application.ui.height-50, padding=0, margin=0)
    pathText = pyos.GUI.Text((0, 40), navigator.path, state.getColorPalette().getColor("item"), 10, width=application.ui.width)
    bar = getDefaultButtonBar()
    application.ui.addChild(bar)
    application.ui.addChild(pathText)
    application.ui.addChild(container)
    load()
