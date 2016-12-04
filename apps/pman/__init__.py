import pyos
import urllib2
from urllib import urlretrieve
from apps.pman.fuzzywuzzy import fuzz
from datetime import timedelta

import time

"""
PMan Specific app.json parameters.
Specified under the key "pman".
{
    "pman": {
        "depends": [] - A list of packages on which the app depends.
        "min_os": 1.0 - A float representing the minimum system version supported.
        "onInstalled": <method> - A method located in your app's module that will be called (with no arguments) after the app is installed.
    }
}
"""

REPOS = []

def loadRepos():
    global REPOS
    REPOS = fetchJSON("apps/pman/repos.json")["repos"]
    
def download(url, to):
    try:
        urlretrieve(url, to)
        return True
    except:
        return False
    
def onStart(s, a):
    global state, app, pman, cache
    state = s
    app = a
    cache = Cache()
    pman = PackageManager()
    pman.openScreen(MainScreen())

def internet_on():
    try:
        urllib2.urlopen('http://www.google.com/', timeout=5)
        return True
    except urllib2.URLError: pass
    return False

def fetchJSON(url):
    try:
        resource = None
        if pyos.os.path.exists(url):
            resource = open(url, "rU")
        else:
            resource = urllib2.urlopen(url)
        text = str(unicode(resource.read(), errors="ignore"))
        resource.close()
        return pyos.json.loads(text)
    except:
        return None
    
def readJSON(path):
    try:
        f = open(path, "rU")
        jsd = pyos.json.loads(str(unicode(f.read(), errors="ignore")))
        f.close()
        return jsd
    except:
        return {"apps": ""}
    
class ProgressDialog(pyos.GUI.Overlay):
    def __init__(self):
        super(ProgressDialog, self).__init__((0, 0), width=app.ui.width, height=app.ui.height, color=state.getColorPalette().getColor("item"))
        self.container.border = 1
        self.container.borderColor = state.getColorPalette().getColor("background")
        self.title = pyos.GUI.Text((2, 2), "PMan is working...", state.getColorPalette().getColor("background"), 16)
        self.text = pyos.GUI.ExpandingMultiLineText((0, 0), "Stand by.", state.getColorPalette().getColor("background"), 16,
                                           width=self.width, height=self.height-60)
        self.tsc = pyos.GUI.TextScrollableContainer((0, 20), self.text, width=self.width, height=self.height-60,
                                                    color=state.getColorPalette().getColor("item"))
        self.clsbtn = pyos.GUI.Button((0, self.height-40), "Hide Progress", width=self.width, height=40,
                                      onClick=self.hide)
        self.notification = None
        self.addChild(self.title)
        self.addChild(self.tsc)
        self.addChild(self.clsbtn)
        
    def update(self, text):
        self.text.setText(text + "\n" + self.text.text)
        self.tsc.refresh()
        if self.notification != None:
            self.notification.text = text
        
    def hide(self, done=False):
        if self.displayed:
            super(ProgressDialog, self).hide()
            if not done:
                self.notification = pyos.PermanentNotification("PMan Status", self.text.text, image=app.getIcon())
                state.getNotificationQueue().push(self.notification)
        
class AppIcon(pyos.GUI.Image):
    def __init__(self, position, appname, w=40, h=40, **data):
        if appname in state.getApplicationList().applications.values():
            super(AppIcon, self).__init__(position, surface=state.getApplicationList().getApp(appname).getIcon(), width=w, height=h, **data)
        else:
            icn = cache.get(appname).get("more", {}).get("icon", "unknown")
            if icn in state.getIcons().icons.values():
                super(AppIcon, self).__init__(position, path="res/icons/"+icn, width=w, height=h, **data)
            else:                    
                if pyos.os.path.exists("temp/pman_"+appname+"_icon.png") or download(cache.get(appname)["remotePath"]+"icon.png", "temp/pman_"+appname+"_icon.png"):
                    try:
                        super(AppIcon, self).__init__(position, path="temp/pman_"+appname+"_icon.png", width=w, height=h, **data)
                    except:
                        super(AppIcon, self).__init__(position, surface=state.getIcons().getLoadedIcon("unknown"), width=w, height=h, **data)
                    
class AppActionButton(pyos.GUI.Button):
    def __init__(self, position, appname, w, h):
        self.app = appname
        super(AppActionButton, self).__init__(position, "", width=w, height=h)
        self.refresh()
        
    def refresh(self):
        if self.app in state.getApplicationList().applications.keys():
            self.backgroundColor = (200, 250, 200)
            if float(cache.get(self.app).get("version", 0.0)) > state.getApplicationList().getApp(self.app).version:
                self.setOnClick(Installer(self.app).start)
                self.setText("Update")
            else:
                self.setOnClick(state.getApplicationList().getApp(self.app).activate)
                self.setText("Open")
        else:
            self.backgroundColor = (200, 200, 250)
            self.setOnClick(Installer(self.app).start)
            self.setText("Install")
        super(AppActionButton, self).refresh()
        
class UIParts:
    @staticmethod
    def smallAppEntry(appname, onC, fits="appui"):
        if fits == "appui": fits = app.ui
        cont = pyos.GUI.Container((0, 0), width=fits.width, height=20, border=1, onClick=onC)
        cont.addChild(AppIcon((0, 0), appname, 20, 20, onClick=onC))
        cont.addChild(pyos.GUI.Text((22, 2), cache.get(appname)["title"], pyos.DEFAULT, 16, onClick=onC))
        cont.addChild(AppActionButton((cont.width-40, 0), appname, 40, 20))
        return cont
    
    @staticmethod
    def normalAppEntry(appname, onC, fits="appui"):
        if fits == "appui": fits = app.ui
        cont = pyos.GUI.Container((0, 0), width=fits.width, height=40, border=1, onClick=onC)
        cont.addChild(AppIcon((0, 0), appname, 40, 40, onClick=onC))
        cont.addChild(pyos.GUI.Text((42, 2), cache.get(appname)["title"], pyos.DEFAULT, 18, onClick=onC))
        cont.addChild(pyos.GUI.Text((42, 22), cache.get(appname)["author"], pyos.DEFAULT, 14, onClick=onC))
        cont.addChild(AppActionButton((cont.width-60, 0), appname, 60, 40))
        return cont
    
    @staticmethod
    def largeAppEntry(appname, onC, fits="appui"):
        if fits == "appui": fits = app.ui
        cont = pyos.GUI.Container((0, 0), width=fits.width, height=64, border=1, onClick=onC)
        cont.addChild(AppIcon((0, 0), appname, 40, 40, onClick=onC))
        cont.addChild(pyos.GUI.Text((42, 2), cache.get(appname)["title"], pyos.DEFAULT, 18, onClick=onC))
        cont.addChild(pyos.GUI.Text((42, 22), cache.get(appname)["author"], pyos.DEFAULT, 14, onClick=onC))
        cont.addChild(AppActionButton((cont.width-60, 0), appname, 60, 40))
        dt = cache.get(appname).get("description", "No Description.")
        cont.addChild(pyos.GUI.MultiLineText((2, 40), dt[:dt.find(".")], pyos.DEFAULT, 12, width=cont.width, height=24))
        return cont
    
class SizeSelector(pyos.GUI.Selector):
    def __init__(self, position, w, h, oVc):
        self.size = app.dataStore.get("sel_size", "Small")
        self.choices = ["Small", "Normal", "Detailed"]
        super(SizeSelector, self).__init__(position, self.getChoices(), width=w, height=h,
                                           onValueChanged=oVc)
        
    def getChoices(self):
        lc = self.choices[:]
        lc.remove(self.size)
        return [self.size] + lc
            
    def getEntry(self, appname, onC, fits="appui"):
        val = self.size
        if val == "Small": return UIParts.smallAppEntry(appname, onC, fits)
        if val == "Normal": return UIParts.normalAppEntry(appname, onC, fits)
        if val == "Detailed": return UIParts.largeAppEntry(appname, onC, fits)
    
class BackBtn(pyos.GUI.Image):
    def __init__(self, position):
        super(BackBtn, self).__init__(position, surface=state.getIcons().getLoadedIcon("back"),
                                      onClick=pman.closeLast)
    
class Screen(pyos.GUI.Container):
    def __init__(self, name):
        self.name = name
        super(Screen, self).__init__((0, 0), width=app.ui.width, height=app.ui.height)
        
    def activate(self):
        if self not in pman.screens:
            pman.openScreen(self)
            return
        self.oldtitle = state.getFunctionBar().app_title_text.text
        state.getFunctionBar().app_title_text.setText(self.name)
        app.ui.clearChildren()
        app.ui.addChild(self)
    
    def deactivate(self):
        state.getFunctionBar().app_title_text.setText(self.oldtitle)
        
class AppScreen(Screen):
    def __init__(self, appname):
        self.appname = appname
        super(AppScreen, self).__init__(cache.get(appname).get("title", appname))
        self.refresh()
        
    def refresh(self):
        self.clearChildren()
        self.data = cache.get(self.appname)
        self.addChild(UIParts.normalAppEntry(self.appname, pyos.Application.dummy))
        self.addChild(pyos.GUI.Text((2, 42), "Package: "+self.appname))
        self.addChild(pyos.GUI.Text((2, 58), "Version "+str(self.data.get("version", 0.0))))
        if self.appname in app.dataStore.get("featured", []): self.addChild(pyos.GUI.Text((2, 74), "Featured", (250, 150, 150)))
        self.addChild(pyos.GUI.MultiLineText((2, 90), self.data.get("description", "No Description"), width=app.ui.width, height=(app.ui.height-130)))
        self.addChild(BackBtn((0, self.height-40)))
        self.addChild(pyos.GUI.Button((40, self.height-40), "More by "+self.data.get("author"),
                                      state.getColorPalette().getColor("dark:background"), width=app.ui.width-40, height=40,
                                      onClick=AppListScreen.ondemand,
                                      onClickData=([a for a in cache.data.keys() if cache.get(a).get("author") == self.data.get("author")],)))
        
class UpdateScreen(Screen):
    def __init__(self):
        super(UpdateScreen, self).__init__("Updates")
        self.refresh()
        
    @staticmethod
    def ondemand():
        UpdateScreen().activate()
        
    def bgLoad(self, sel=None):
        if sel != None: app.dataStore["sel_size"] = sel
        self.removeChild(self.sizesel)
        self.sizesel = SizeSelector((app.ui.width-100, 0), 100, 40, self.bgLoad)
        self.addChild(self.sizesel)
        self.scroller.clearChildren()
        txt = pyos.GUI.Text((0, 0), "Loading...")
        self.scroller.addChild(txt)
        au = 0
        for lapp in sorted(state.getApplicationList().getApplicationList(), key=lambda x: x.title):
            if cache.get(lapp.name).get("version", 0.0) > lapp.version:
                self.scroller.addChild(self.sizesel.getEntry(lapp.name, AppScreen(lapp.name).activate, self.scroller.container))
                au += 1
        self.statustxt.setText(str(au)+" Updates")
        self.scroller.removeChild(txt)
        
    def refresh(self):
        self.clearChildren()
        self.scroller = pyos.GUI.ListScrollableContainer((0, 40), width=app.ui.width, height=app.ui.height-40)
        self.statustxt = pyos.GUI.Text((42, 11), "0 Updates", pyos.DEFAULT, 18)
        self.back = BackBtn((0, 0))
        self.sizesel = SizeSelector((app.ui.width-100, 0), 100, 40, self.bgLoad)
        self.addChildren(self.scroller, self.statustxt, self.back, self.sizesel)
        state.getThreadController().addThread(pyos.ParallelTask(self.bgLoad))
        
class AppListScreen(Screen):
    def __init__(self, apps):
        self.apps = apps
        super(AppListScreen, self).__init__("Apps")
        self.refresh()
        
    @staticmethod
    def ondemand(apps):
        AppListScreen(apps).activate()
        
    def bgLoad(self, sel=None):
        if sel != None: app.dataStore["sel_size"] = sel
        self.removeChild(self.sizesel)
        self.sizesel = SizeSelector((app.ui.width-100, 0), 100, 40, self.bgLoad)
        self.addChild(self.sizesel)
        self.scroller.clearChildren()
        txt = pyos.GUI.Text((0, 0), "Loading...")
        self.scroller.addChild(txt)
        au = 0
        for a in sorted(self.apps, key=lambda x: cache.get(x, {"title": x}).get("title")):
            self.scroller.addChild(self.sizesel.getEntry(a, AppScreen(a).activate, self.scroller.container))
            au += 1
        self.statustxt.setText(str(au)+" Apps")
        self.scroller.removeChild(txt)
        
    def refresh(self):
        self.clearChildren()
        self.scroller = pyos.GUI.ListScrollableContainer((0, 40), width=app.ui.width, height=app.ui.height-40)
        self.statustxt = pyos.GUI.Text((42, 11), "0 Apps", pyos.DEFAULT, 18)
        self.back = BackBtn((0, 0))
        self.sizesel = SizeSelector((app.ui.width-100, 0), 100, 40, self.bgLoad)
        self.addChildren(self.scroller, self.statustxt, self.back, self.sizesel)
        state.getThreadController().addThread(pyos.ParallelTask(self.bgLoad))
        
class SearchScreen(Screen):
    def __init__(self, query):
        self.query = query.lower()
        super(SearchScreen, self).__init__("Search Results")
        self.refresh()
        
    @staticmethod
    def ondemand(query):
        SearchScreen(query).activate()
        
    def bgLoad(self, sel=None):
        if sel != None: app.dataStore["sel_size"] = sel
        self.removeChild(self.sizesel)
        self.sizesel = SizeSelector((app.ui.width-80, 0), 80, 40, self.bgLoad)
        self.addChild(self.sizesel)
        self.scroller.clearChildren()
        txt = pyos.GUI.Text((0, 0), "Loading...")
        self.scroller.addChild(txt)
        results = {}
        for a in cache.data.keys():
            r = fuzz.ratio(self.query, a)
            r += fuzz.ratio(self.query, cache.get(a).get("title").lower())
            r += fuzz.token_sort_ratio(self.query, cache.get(a).get("description", "").lower())
            ar = fuzz.ratio(self.query, cache.get(a).get("author", "").lower())
            if r >110 or ar > 60:
                results[a] = r+ar
        for ra in sorted(results.keys(), key=lambda x: results[x], reverse=True):
            self.scroller.addChild(self.sizesel.getEntry(ra, AppScreen(ra).activate, self.scroller.container))
        self.scroller.removeChild(txt)
        
    def setQuery(self):
        self.query = self.statustxt.getText().lower()
        pman.refresh()
        
    def refresh(self):
        self.clearChildren()
        self.scroller = pyos.GUI.ListScrollableContainer((0, 40), width=app.ui.width, height=app.ui.height-40)
        self.statustxt = pyos.GUI.TextEntryField((40, 0), self.query, width=self.width-160, height=40)
        self.submitbtn = pyos.GUI.Image((self.width-120, 0), surface=state.getIcons().getLoadedIcon("search"),
                                        onClick=self.setQuery)
        self.back = BackBtn((0, 0))
        self.sizesel = SizeSelector((app.ui.width-80, 0), 80, 40, self.bgLoad)
        self.addChildren(self.scroller, self.statustxt, self.submitbtn, self.back, self.sizesel)
        state.getThreadController().addThread(pyos.ParallelTask(self.bgLoad))
        
class MainScreen(Screen):
    def __init__(self):
        super(MainScreen, self).__init__("Apps")
        self.refresh()
        
    def refresh(self):
        self.clearChildren()
        if internet_on():
            self.addChild(pyos.GUI.Button((40, self.height-80), "Update Database", (107, 148, 103), width=self.width-40, height=40,
                                          onClick=cache.bgUpdate))
            self.addChild(pyos.GUI.Image((0, self.height-80), surface=state.getIcons().getLoadedIcon("save"),
                                     onClick=cache.bgUpdate))
            self.featuredHerald = pyos.GUI.Container((0, 0), width=self.width, height=20, color=(51, 183, 255))
            self.featuredHerald.addChild(pyos.GUI.Text((2, 2), "Featured Apps", pyos.DEFAULT, 16))
            self.featuredShowcase = pyos.GUI.ListPagedContainer((0, 20), width=self.width, height=90,
                                                                border=1, borderColor=(51, 183, 255))
            if app.dataStore.get("featured", []) == []:
                self.featuredShowcase.addChild(pyos.GUI.Text((5, 5), "No Featured Apps."))
            else:
                for fa in app.dataStore.get("featured", []):
                    self.featuredShowcase.addChild(UIParts.largeAppEntry(fa, AppScreen(fa).activate))
            self.featuredShowcase.goToPage()
            self.addChild(self.featuredHerald)
            self.addChild(self.featuredShowcase)
            self.addChild(pyos.GUI.Button((0, self.height-120), "Updates", (255, 187, 59), width=self.width/2, height=40,
                                          onClick=UpdateScreen.ondemand))
            self.addChild(pyos.GUI.Button((self.width/2, self.height-120), "All Apps", (148, 143, 133), width=self.width/2, height=40,
                                          onClick=AppListScreen.ondemand, onClickData=(cache.data.keys(),)))
            self.searchBar = pyos.GUI.TextEntryField((0, self.height-160), "", width=self.width-40, height=40)
            self.addChild(pyos.GUI.Image((self.width-40, self.height-160), surface=state.getIcons().getLoadedIcon("search"),
                                         onClick=self.search))
            self.addChild(self.searchBar)
            
        self.addChild(pyos.GUI.Image((0, self.height-40), surface=state.getIcons().getLoadedIcon("open"),
                                      onClick=Installer.localAsk))
        self.addChild(pyos.GUI.Button((40, self.height-40), "Install from File", (194, 89, 19), width=self.width-40, height=40,
                                      onClick=Installer.localAsk))
        
    def search(self):
        SearchScreen.ondemand(self.searchBar.getText())
        
    
class Cache(pyos.DataStore):
    def __init__(self, doDialog=True):
        self.dsPath = "apps/pman/cache.json"
        self.application = app
        self.featured = []
        self.progressInfo = "Updating Cache"
        self.dialog = None if not doDialog else ProgressDialog()
        self.data = {}
        
    def setPrgInfo(self, txt):
        print txt
        self.progressInfo = txt
        if self.dialog != None:
            self.dialog.update(txt)
            if txt == "Done.":
                self.dialog.hide(True)
                self.dialog = ProgressDialog()
        
    def update(self):
        self.data = {}
        self.featured = []
        if self.dialog != None:
            self.dialog.display()
        self.saveStore()
        cr = 0
        for repo in REPOS:
            cr += 1
            self.setPrgInfo("R("+str(cr)+"): "+repo)
            if download(repo+"/apps.json", "temp/apps.json"):
                ca = 0
                rman = readJSON("temp/apps.json")
                for rapp in rman["apps"]:
                    ca += 1
                    self.setPrgInfo("R("+str(cr)+") A("+str(ca)+"): "+rapp)
                    if download(repo+"/"+rman["apps_dir"]+"/"+rapp+"/app.json", "temp/app.json"):
                        aman = readJSON("temp/app.json")
                        aman["remotePath"] = repo+"/"+rman["apps_dir"]+"/"+rapp+"/"
                        self.set(rapp, aman)
                finf = rman.get("featured", None)
                if finf != None:
                    if isinstance(finf, basestring):
                        self.featured.append(rman["featured"])
                    else:
                        for f in rman["featured"]: self.featured.append(f)
                for f in rman.get("featured_list", []): self.featured.append(f)
        self.setPrgInfo("Cleaning Up...")
        try:
            pyos.os.remove("temp/apps.json")
            pyos.os.remove("temp/app.json")
            for trc in pyos.os.listdir("temp/"):
                if trc.startswith("pman_"):
                    pyos.os.remove("temp/"+trc)
        except:
            pass
        app.dataStore["lastUpdate"] = pyos.datetime.strftime(pyos.datetime.now(), "%a %b %d %H:%M:%S %Y")
        app.dataStore["featured"] = self.featured
        self.setPrgInfo("Done.")
        pman.refresh()
        
    def bgUpdate(self):
        state.getThreadController().addThread(pyos.ParallelTask(self.update))
        
class Installer(object):
    def __init__(self, appname, local=False):
        self.local = local
        self.name = appname
        
    def start(self):
        if self.local:
            try:
                zf = pyos.ZipFile(self.name, "r")
                zf.extract("app.json", "temp/pman_app.json")
                self.path = self.name
                jd = readJSON("temp/pman_app.json")
                self.name = jd["name"]
                if jd.get("pman", {}).get("min_os", 0.0) > pman.sysInf.get("version"):
                    pyos.GUI.ErrorDialog("The package requires a newer version of Python OS.").display()
                    return
            except:
                pyos.GUI.ErrorDialog("The file "+self.name+" is not a valid Python OS ZIP File.").display()
                return
        pyos.GUI.YNDialog("Install", 
                          "Are you sure you want to install the package "+self.name+"? This will install the app and any unmet dependencies.",
                          self.confirm).display()
        self.dialog = ProgressDialog()
        
    @staticmethod
    def localInstallSelect(path):
        Installer(path, True)
        
    @staticmethod
    def localAsk():
        state.getApplicationList().getApp("files").getModule().FilePicker((10, 10), app, width=app.ui.width-20, height=app.ui.height-20,
                                                                          onSelect=Installer.localInstallSelect).display()
        
    @staticmethod
    def getDependencies(appname, deps=[], oan=None):
        if deps == []: 
            deps = cache.get(appname).get("pman", {}).get("depends", [])
            oan = appname
        print appname + " depends on " + str(deps)
        print deps
        for d in deps:
            if d == appname:
                print "Warning: The app "+appname+" depends on itself."
                continue
            sd = Installer.getDependencies(d, [], oan)
            for s in sd:
                if s == oan:
                    print "Warning: The dependency of "+appname+", "+s+", depends on the original package "+oan+"."
                    continue
                if (s not in deps) or (s in state.getApplicationList().getApplicationList() and cache.get(s).get("version") > state.getApplicationList().getApp(s).version):
                    deps.append(s)
        return deps
        
    def confirm(self, resp):
        if resp == "Yes":
            self.dialog.display()
            self.dialog.update("Requested install of "+self.name)
            state.getThreadController().addThread(pyos.ParallelTask(self.install))
            
    def install(self):
        deps = Installer.getDependencies(self.name)
        toinst = [self.name] + deps
        post_install = []
        for tia in toinst:
            if cache.get(tia).get("pman", {}).get("min_os", 0.0) > pman.sysInf.get("version"):
                self.dialog.update("!!! The install cannot continue because the package "+tia+" requires a newer version of Python OS.")
                return
            pim = cache.get(tia).get("pman", {}).get("onInstalled", None)
            if pim != None:
                post_install.append([tia, pim])
        if tia == []:
            print self.name+" and all its dependencies are already installed."
            return
        self.dialog.update("The following packages will be installed:")
        for p in toinst:
            self.dialog.update(" - "+p)
        c = 0
        for package in toinst:
            self.dialog.update(str(c)+": Working on "+package)
            if package == self.name and self.local:
                self.dialog.update("... Installing from local package.")
                try:
                    self.dialog.update("... Installed.")
                    pyos.Application.install(self.path)
                except:
                    self.dialog.update("!!! Install failed. Aborted.")
                    break
                try:
                    pyos.os.remove("temp/pman_app.json")
                except:
                    pass
                c += 1
                continue
            if download(cache.get(package)["remotePath"]+package+".zip", "temp/pman_package.zip"):
                self.dialog.update("... Downloaded.")
                try:
                    pyos.Application.install("temp/pman_package.zip")
                    self.dialog.update("... Installed.")
                except:
                    self.dialog.update("!!! Install failed. Aborted.")
                    break
            else:
                self.dialog.update("!!! Download failed. Install aborted.")
                break
            c += 1
        self.dialog.update("Running post-install operations...")
        for pia in post_install:
            try:
                getattr(state.getApplicationList().getApp(pia[0]).getModule(), pia[1])()
                self.dialog.update("... "+pia[0])
            except:
                self.dialog.update("!!! Error running. "+pia[0]+" might be broken.")
        self.dialog.update("Finished. Cleaning up...")
        try:
            pyos.os.remove("temp/pman_package.zip")
        except:
            pass
        state.getApplicationList().reloadList()
        self.dialog.update("Done.")
        self.dialog.hide(True)
        pman.refresh()
        
class PackageManager(object):
    def __init__(self):
        self.screens = []
        self.sysInf = readJSON("res/system.json")
        loadRepos()
        self.checkDBFresh()
        
    def refresh(self):
        self.screens[len(self.screens)-1].refresh()
        
    def checkDBFresh(self):
        lupd = app.dataStore.get("lastUpdate", None)
        try:
            if len(cache.getStore().keys()) <= 1:
                print "Empty Cache"
                app.dataStore.set("featured", [])
                raise AttributeError
        except:
            lupd = None
        if lupd != None: diffdel = (pyos.datetime.now() - pyos.datetime.strptime(lupd, "%a %b %d %H:%M:%S %Y"))
        if lupd == None or diffdel > timedelta(days=1):
            cache.bgUpdate()
        
    def openScreen(self, s):
        self.screens.append(s)
        s.activate()
        
    def closeLast(self):
        self.screens.pop().deactivate()
        self.screens[len(self.screens)-1].activate()
