import pyos
import urllib2
from urllib import urlretrieve
from apps.pman.fuzzywuzzy import fuzz
import traceback

REPOSITORY = "https://raw.githubusercontent.com/furmada/PythonOSApps/gh-pages/"

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
        resource = urllib2.urlopen(REPOSITORY+url)
        text = str(unicode(resource.read(), errors="ignore"))
        return pyos.json.loads(text)
    except:
        return None
    
def fetchPackage(app):
    try:
        urlretrieve(REPOSITORY+pman.repoPath+app+"/"+app+".zip", "temp/pmanTmpPkg.zip")
        return "temp/pmanTmpPkg.zip"
    except:
        print "Error accessing "+REPOSITORY+pman.repoPath+app+"/"+app+".zip"
        return None
    
def getIcon(app):
    try:
        urlretrieve(REPOSITORY+pman.repoPath+app+"/icon.png", "temp/pmanTmpIcon.png")
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
            self.installBtn = pyos.GUI.Button((self.width-80, 80), "Install", (100, 100, 250), (20, 20, 20), 24, width=80, height=40,
                                              onClick=PackageManager.installAsk, onClickData=(app,))
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
                self.featuredContainer.addChild(pyos.GUI.Text((2, 82), "Ver.: "+str(featured_data["version"]), (20, 20, 20), 14))
                self.featuredContainer.addChild(pyos.GUI.Text((2, 100), "Featured App", (200, 50, 50), 14))
                self.featuredContainer.addChild(pyos.GUI.MultiLineText((82, 40), featured_data.get("description", "No Description")[:featured_data.get("description", "No Description").find(".")], (20, 20, 20), 14,
                                                                       width=self.width-82, height=80))
                self.addChild(self.featuredContainer)
                
                self.allAppsLink = pyos.GUI.Container((0, 120), width=self.width-40, height=40, color=(20, 20, 20),
                                                      onClick=self.loadAllApps)
                self.allAppsLink.SKIP_CHILD_CHECK = True
                self.allAppsLink.addChild(pyos.GUI.Text((2, 6), "All Apps", (200, 200, 200), 24))
                self.addChild(self.allAppsLink)
                self.addChild(pyos.GUI.Image((self.width-40, self.allAppsLink.position[1]), surface=state.getIcons().getLoadedIcon("search"),
                                                         onClick=self.appSearchAsk))
                
                self.updatesLink = pyos.GUI.Container((0, 160), width=self.width, height=40, color=(20, 150, 20),
                                                      onClick=self.loadUpdates)
                self.updatesLink.SKIP_CHILD_CHECK = True
                self.updatesLink.addChild(pyos.GUI.Text((2, 6), "Updates", (200, 200, 200), 24))
                self.addChild(self.updatesLink)
            else:
                pyos.GUI.ErrorDialog("Unable to load the repository manifest.").display()
        self.localLink = pyos.GUI.Container((0, 200), width=self.width, height=40, color=(20, 20, 150),
                                            onClick=self.installPkgLocAsk)
        self.localLink.SKIP_CHILD_CHECK = True
        self.localLink.addChild(pyos.GUI.Text((2, 6), "Install from File", (200, 200, 200), 24))
        self.addChild(self.localLink)
                
    def reset(self):
        self = MainPage(self.width, self.height, self.backgroundColor)
        
    def loadAllApps(self):
        pman.openPage(AppListPage("All Apps", self.applist["apps"], self.width, self.height, self.backgroundColor))
        
    def loadUpdates(self):
        pman.openPage(UpdateListPage("Updates", self.width, self.height, self.backgroundColor))
        
    def installPkgLocAsk(self):
        state.getApplicationList().getApp("files").getModule().FilePicker((10, 10), app, width=app.ui.width-20, height=app.ui.height-20,
                                                                          onSelect=PackageManager.installLocalAsk).display()
                                                                          
    def appSearchAsk(self):
        pyos.GUI.AskDialog("Search", "Enter the package name to search for.", self.appSearch).display()
        
    def appSearch(self, query):
        results = []
        for a in pman.repoApps:
            ratio = fuzz.ratio(a, query)
            if ratio <= 50: continue
            if len(results) == 0 or ratio > results[0][1]:
                results.insert(0, [a, ratio])
            else:
                if ratio == results[0][1]:
                    results.insert(1, [a, ratio])
                else:
                    results.append([a, ratio])
        if results != []:
            pman.openPage(AppListPage("Search: "+query, [a[0] for a in results], self.width, self.height, self.backgroundColor, False))
        else:
            pyos.GUI.OKDialog("No Results", "Your search returned no relevant results.").display()
                
class AppListPage(Page):    
    def __init__(self, title, alist, w, h, c, alpha=True):
        super(AppListPage, self).__init__(w, h, c)
        self.title = title
        self.pages = pyos.GUI.ListPagedContainer((0, 0), width=self.width, height=self.height, color=self.backgroundColor, margin=0)
        toload = []
        listToUse = []
        if alpha: listToUse = sorted(alist)
        else: listToUse = alist
        for a in listToUse:
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
                localApp = state.getApplicationList().getApp(a)
                icn = localApp.getIcon()
                if icn == False: icn = state.getIcons().getLoadedIcon("unknown")
                icon.setImage(surface=icn)
                title.setText(localApp.title)
                author.setText(localApp.author)
            else:
                inst_btn = pyos.GUI.Button((container.width-60, 0), "Install", (100, 100, 250), (20, 20, 20), 18, width=60, height=40,
                                           onClick=PackageManager.installAsk, onClickData=(a,))
                toload.append([a, title, author, icon])
            container.addChild(icon)
            container.addChild(title)
            container.addChild(author)
            container.addChild(inst_btn)
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
            
class UpdateListPage(Page):    
    def __init__(self, title, w, h, c):
        super(UpdateListPage, self).__init__(w, h, c)
        self.title = title
        self.scroller = pyos.GUI.ListScrollableContainer((0, 0), width=self.width, height=self.height, color=self.backgroundColor, scrollAmount=40)
        toload = []
        for a in [a.name for a in state.getApplicationList().getApp("launcher").getModule().alphabetize(state.getApplicationList().getApplicationList())]:
            container = pyos.GUI.Container((0, 0), width=self.scroller.container.width, height=40, color=self.backgroundColor, border=1, borderColor=(20, 20, 20))
            icon = pyos.GUI.Image((0, 0), surface=state.getIcons().getLoadedIcon("unknown"), width=40, height=40,
                                  onClick=AppPage.addAppPage, onClickData=(a,))
            title = pyos.GUI.Text((42, 0), "Application", state.getColorPalette().getColor("item"), 24,
                                  onClick=AppPage.addAppPage, onClickData=(a,))
            author = pyos.GUI.Text((42, 24), "Author", (20, 20, 20), 14,
                                   onClick=AppPage.addAppPage, onClickData=(a,))
            inst_btn = pyos.GUI.Button((container.width-60, 0), "Latest", (100, 250, 100), (20, 20, 20), 18, width=60, height=40,
                                          onClick=state.getApplicationList().getApp(a).activate)
            localApp = state.getApplicationList().getApp(a)
            try:
                icon.setImage(surface=localApp.getIcon())
            except:
                icon.setImage(surface=state.getIcons().getLoadedIcon("unknown"))
            title.setText(localApp.title)
            author.setText(localApp.author)
            toload.append([a, container, title, author, icon, inst_btn])
            container.addChild(icon)
            container.addChild(title)
            container.addChild(author)
            container.addChild(inst_btn)
            self.scroller.addChild(container)
        self.addChild(self.scroller)
        loadTask = pyos.ParallelTask(self.loadList, toload)
        state.getThreadController().addThread(loadTask)

    def loadList(self, toload):
        newOrder = []
        for item in toload:
            manifest = AppPage.getAppInfo(item[0])
            if manifest == None:
                continue
            localApp = state.getApplicationList().getApp(item[0])
            if manifest["version"] > localApp.version:
                item[2].setText(manifest["title"])
                item[3].setText(manifest["author"])
                item[5].backgroundColor = (100, 100, 250)
                item[5].setText("Update")
                item[5].eventBindings["onClick"] = PackageManager.updateAsk
                item[5].eventData["onClick"] = (item[0],)
                newOrder.insert(0, item[1])
            else:
                newOrder.append(item[1])
        self.scroller.clearChildren()
        for child in newOrder:
            self.scroller.addChild(child)
    
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
        
        if app.file != None:
            PackageManager.installLocalAsk(app.file)
            app.file = None
        
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
            
    @staticmethod
    def installLocalAsk(pkgloc):
        pyos.GUI.YNDialog("Install", "Are you sure you wish to install an application from the local package "+pkgloc[pkgloc.rfind("/")+1:]+"?",
                          PackageManager.installLocal, (pkgloc,)).display()
                          
    @staticmethod
    def installLocal(pkgloc, resp):
        if resp != "Yes": return
        app = ""
        try:
            app = pyos.Application.install(pkgloc)
        except:
            pyos.GUI.ErrorDialog("Error while installing the package.").display()
            return
        state.getApplicationList().reloadList()
        state.getNotificationQueue().push(pyos.Notification("App Installed", "Installed "+app, 
                                                            source=state.getApplicationList().getApp(app),
                                                            image=state.getApplicationList().getApp(app).getIcon()))
            
    @staticmethod
    def installAsk(app):
        pyos.GUI.YNDialog("Install", "Are you sure you want to install the package "+app+" on your device?", PackageManager.install, (app,)).display()
        
    @staticmethod
    def updateAsk(app):
        pyos.GUI.YNDialog("Install", "Are you sure you want to update the package "+app+"?", PackageManager.install, (app,)).display()
        
    @staticmethod
    def installThread(app):
        package = fetchPackage(app)
        if package == None:
            pyos.GUI.ErrorDialog("Could not fetch the package.").display()
            return
        try:
            pyos.Application.install(package)
        except:
            pyos.GUI.ErrorDialog("Error while installing the package.").display()
            traceback.print_exc()
            return
        state.getApplicationList().reloadList()
        state.getNotificationQueue().push(pyos.Notification("App Installed", "Installed "+app, 
                                                            source=state.getApplicationList().getApp(app),
                                                            image=state.getApplicationList().getApp(app).getIcon()))
        
    @staticmethod
    def install(app, resp):
        if resp == "Yes":
            task = pyos.ParallelTask(PackageManager.installThread, app)
            state.getThreadController().addThread(task)
            pman.closeCurrentPage()
            
                
            