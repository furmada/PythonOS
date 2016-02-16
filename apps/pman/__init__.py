import pyos
import urllib2

REPOSITORY = "http://www.github.com/furmada/PythonOSApps/raw/gh-pages/"

def onStart(s, a):
    global state, app, pman
    state = s
    app = a
    PackageManager()

def internet_on():
    try:
        urllib2.urlopen('http://74.125.224.72/', timeout=1)
        return True
    except urllib2.URLError: pass
    return False

def fetchJSON(url):
    try:
        text = urllib2.urlopen(REPOSITORY+url).read()
        return pyos.json.loads(text)
    except:
        return None
    
def getIcon(app):
    try:
        icdata = urllib2.urlopen(REPOSITORY+pman.repoPath+app+"/icon.png")
        ictf = open("temp/pmanTmpIcon.png", "wb")
        ictf.write(icdata.read())
        ictf.close()
        return pyos.pygame.image.load("temp/pmanTmpIcon.png")
    except:
        print "Error accessing "+REPOSITORY+pman.repoPath+app+"/icon.png"
        return state.getIcons().getLoadedIcon("unknown")

class Page(pyos.GUI.Container):
    def __init__(self, w, h, c):
        super(Page, self).__init__((0, 0), width=w, height=h, color=c)
        self.title = "Page"
        
class AppPage(Page):
    @staticmethod
    def getAppInfo(app):
        return fetchJSON(pman.repoPath+app+"/app.json")
    
    @staticmethod
    def addAppPage(app):
        pman.openPage(AppPage(app, pman.pageContainer.width, pman.pageContainer.height, (250, 250, 250)))
            
    def __init__(self, app, w, h, c):
        state.getGUI().displayStandbyText("Loading...")
        super(AppPage, self).__init__(w, h, c)
        self.manifest = AppPage.getAppInfo(app)
        self.title = self.manifest["title"]
        self.addChild(pyos.GUI.Image((0, 0), surface=getIcon(app), width=80, height=80))
        self.addChild(pyos.GUI.Text((82, 0), self.manifest["title"], (20, 20, 20), 24))
        self.addChild(pyos.GUI.Text((82, 26), self.manifest["author"], (20, 20, 20), 14))
        self.addChild(pyos.GUI.Text((82, 42), "Ver.: "+str(self.manifest["version"]), (20, 20, 20), 14))
        self.addChild(pyos.GUI.Text((2, 93), "Package Name: "+self.manifest["name"], (20, 20, 20), 14))
        self.installBtn = None
        if app in pman.installedApps:
            self.installBtn = pyos.GUI.Button((self.width-80, 80), "Open", (100, 250, 100), (20, 20, 20), 24, width=80, height=40,
                                              onClick=state.getApplicationList().getApp(self.manifest["name"]).activate)
        else:
            self.installBtn = pyos.GUI.Button((self.width-80, 80), "Install", (100, 100, 250), (20, 20, 20), 24, width=80, height=40)
        self.addChild(self.installBtn)
        self.addChild(pyos.GUI.MultiLineText((2, 120), self.manifest.get("description", "No Description"), (20, 20, 20), 14,
                                            width=self.width-4, height=self.height-20))

class MainPage(Page):
    def __init__(self, w, h, c):
        super(MainPage, self).__init__(w, h, c)
        self.title = "Software Manager"
        if not internet_on():
            self.addChild(pyos.GUI.Text((2, 2), "No Internet connection.", (250, 100, 100), 24,
                                        onClick=self.reset))
        else:
            self.applist = fetchJSON("apps.json")
            state.getGUI().displayStandbyText("Loading...")
            if self.applist != None:
                pman.repoPath = self.applist["apps_dir"]+"/"
                pman.repoApps = self.applist["apps"]
                featured_data = AppPage.getAppInfo(self.applist["featured"])
                self.featuredContainer = pyos.GUI.Container((0, 0), width=self.width, height=120, color=(250, 250, 250),
                                                            onClick=AppPage.addAppPage,
                                                            onClickData=(self.applist["featured"],))
                self.featuredContainer.SKIP_CHILD_CHECK = True
                self.featuredContainer.addChild(pyos.GUI.Image((0, 0), surface=getIcon(self.applist["featured"]), width=80, height=80))
                self.featuredContainer.addChild(pyos.GUI.Text((82, 0), featured_data["title"], (20, 20, 20), 24))
                self.featuredContainer.addChild(pyos.GUI.Text((82, 26), featured_data["author"], (20, 20, 20), 14))
                self.featuredContainer.addChild(pyos.GUI.Text((2, 88), "Ver.: "+str(featured_data["version"]), (20, 20, 20), 14))
                self.featuredContainer.addChild(pyos.GUI.MultiLineText((82, 40), featured_data.get("description", "No Description")[:featured_data.get("description", "No Description").find(".")], (20, 20, 20), 14,
                                                                       width=self.width-82, height=80))
                self.addChild(self.featuredContainer)
                
                self.allAppsLink = pyos.GUI.Container((0, 120), width=self.width, height=40, color=(20, 20, 20),
                                                      onClick=self.loadAllApps)
                self.allAppsLink.SKIP_CHILD_CHECK = True
                self.allAppsLink.addChild(pyos.GUI.Text((2, 6), "All Apps", (200, 200, 200), 24))
                self.addChild(self.allAppsLink)
                
    def reset(self):
        self = MainPage(self.width, self.height, self.backgroundColor)
        
    def loadAllApps(self):
        pman.openPage(AppListPage("All Apps", self.applist["apps"], self.width, self.height, self.backgroundColor))
                
class AppListPage(Page):    
    def __init__(self, title, alist, w, h, c):
        super(AppListPage, self).__init__(w, h, c)
        self.title = title
        self.pages = pyos.GUI.ListPagedContainer((0, 0), width=self.width, height=self.height, color=self.backgroundColor)
        toload = []
        for a in alist:
            container = pyos.GUI.Container((0, 0), width=self.width, height=40, color=self.backgroundColor, border=1, borderColor=(20, 20, 20))
            icon = pyos.GUI.Image((0, 0), surface=state.getIcons().getLoadedIcon("unknown"), width=40, height=40,
                                  onClick=AppPage.addAppPage, onClickData=(a,))
            title = pyos.GUI.Text((42, 0), "Application", state.getColorPalette().getColor("item"), 24,
                                  onClick=AppPage.addAppPage, onClickData=(a,))
            author = pyos.GUI.Text((42, 24), "Author", (20, 20, 20), 14,
                                   onClick=AppPage.addAppPage, onClickData=(a,))
            inst_btn = None
            if a in pman.installedApps:
                inst_btn = pyos.GUI.Button((container.width-60, 0), "Open", (100, 250, 100), (20, 20, 20), 18, width=60, height=40,
                                              onClick=state.getApplicationList().getApp(a).activate)
            else:
                inst_btn = pyos.GUI.Button((container.width-60, 0), "Install", (100, 100, 250), (20, 20, 20), 18, width=60, height=40)
            container.addChild(icon)
            container.addChild(title)
            container.addChild(author)
            container.addChild(inst_btn)
            toload.append([a, title, author, icon])
            self.pages.addChild(container)
        self.addChild(self.pages)
        self.pages.goToPage()
        loadTask = pyos.ParallelTask(self.loadList, toload)
        state.getThreadController().addThread(loadTask)
        
    def loadList(self, toload):
        for item in toload:
            manifest = AppPage.getAppInfo(item[0])
            item[1].setText(manifest["title"])
            item[2].setText(manifest["author"])
        for item in toload:
            item[3].setImage(surface=getIcon(item[0]))
    
class PackageManager(object):
    def __init__(self):
        global pman
        pman = self
        
        state.getGUI().displayStandbyText("Accessing database...")
        
        self.pageHistory = []
        self.repoPath = ""
        self.repoApps = []
        
        self.installedApps = [a.name for a in state.getApplicationList().getApplicationList()]
        
        self.pageContainer = pyos.GUI.Container((0, 40), width=app.ui.width, height=app.ui.height-40, color=state.getColorPalette().getColor("background"))
        self.titleContainer = pyos.GUI.Container((0, 0), width=app.ui.width, height=40, color=(100, 100, 250), border=1, borderColor=(100, 100, 250))
        self.titleText = pyos.GUI.Text((45, 11), "Application Manager", state.getColorPalette().getColor("item"), 18)
        self.backButton = pyos.GUI.Image((0, 0), surface=state.getIcons().getLoadedIcon("back"), width=40, height=40,
                                         onClick=self.closeCurrentPage)
        
        self.titleContainer.addChild(self.backButton)
        self.titleContainer.addChild(self.titleText)
        
        app.ui.addChild(self.pageContainer)
        app.ui.addChild(self.titleContainer)
        
        self.openPage(MainPage(self.pageContainer.width, self.pageContainer.height, self.pageContainer.backgroundColor))
        
    def openPage(self, page):
        self.titleText.setText(page.title)
        self.pageHistory.append(page)
        self.pageContainer.clearChildren()
        self.pageContainer.addChild(page)
        
    def closeCurrentPage(self):
        if len(self.pageHistory) > 1:
            self.pageHistory.pop()
            self.pageContainer.clearChildren()
            self.pageContainer.addChild(self.pageHistory[len(self.pageHistory)-1])
            self.titleText.setText(self.pageHistory[len(self.pageHistory)-1].title)
            