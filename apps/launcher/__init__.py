import pyos

application = None

def alphabetize(apps):
    appd = {}
    for a in apps: appd[a.title] = a
    return [appd[a] for a in sorted(appd)]

def getVisibleAppList():
    visible = []
    for app in state.getApplicationList().getApplicationList():
        if app.getIcon() != False and not app.parameters.get("hide", False):
            visible.append(app)
    return visible

def displayInfoDialog(app):
    cont = pyos.GUI.Container((20, 40), width=application.ui.width-40, height=application.ui.height-80, backgroundColor=state.getColorPalette().getColor("background"),
                              border=3, borderColor=state.getColorPalette().getColor("accent"))
    img = pyos.GUI.Image((3, 3), surface=app.getIcon())
    title = pyos.GUI.Text((46, 13), app.title, state.getColorPalette().getColor("item"), 20)
    pkt = pyos.GUI.Text((3, 46), "Package: "+app.name, state.getColorPalette().getColor("item"), 14)
    vert = pyos.GUI.Text((3, 64), "Version: "+str(app.version), state.getColorPalette().getColor("item"), 14)
    aut = pyos.GUI.Text((3, 82), "Author: "+app.author, state.getColorPalette().getColor("item"), 14)
    desct = pyos.GUI.MultiLineText((3, 100), app.description, state.getColorPalette().getColor("item"), 14, width=cont.width-6, height=cont.height-146)
    cont.addChild(img)
    cont.addChild(title)
    cont.addChild(pkt)
    cont.addChild(vert)
    cont.addChild(aut)
    cont.addChild(desct)
    dialog = pyos.GUI.CustomContentDialog("App Info", cont, ["Uninstall", "Open", "Close"], parseDialogAction, 0, 1,
                                          onResponseRecordedData=(app,))
    dialog.display()
    
def parseDialogAction(app, selected):
    if selected == "Open":
        app.activate()
    if selected == "Uninstall":
        uninstallAsk(app)

def uninstallAsk(app):
    if app in state.getApplicationList().activeApplications:
        pyos.GUI.WarningDialog("The app "+app.title+" cannot be uninstalled because it is currently running.").display()
        return
    pyos.GUI.YNDialog("Uninstall", "Are you sure you wish to permanently uninstall "+app.title+"?", uninstall, (app,)).display()
    
def uninstall(app, resp):
    if resp == "Yes":
        app.uninstall()
        state.getApplicationList().reloadList()
        application.ui.clearChildren()
        loadApps(state, application)
        state.getNotificationQueue().push(pyos.Notification("Uninstalled", "The app "+app.title+" is gone.", image=state.getIcons().getLoadedIcon("menu")))

def loadApps(pstate, app):
    global application, state
    state = pstate
    application = state.getActiveApplication()
    application.ui.backgroundColor = state.getColorPalette().getColor("background")
    pagedContainer = pyos.GUI.GriddedPagedContainer((0, 0), 4, width=application.ui.width, height=application.ui.height, color=state.getColorPalette().getColor("background"))
    for app in alphabetize(getVisibleAppList()):
        appPane = None
        if app in state.getApplicationList().activeApplications:
            appPane = pyos.GUI.Container((0, 0), color=state.getColorPalette().getColor("accent")+(100,), width=pagedContainer.perColumn, height=pagedContainer.perRow,
                                         onClick=app.activate, onLongClick=displayInfoDialog, onLongClickData=(app,))
        else:
            appPane = pyos.GUI.Container((0, 0), transparent=True, width=pagedContainer.perColumn, height=pagedContainer.perRow,
                                         onClick=app.activate, onLongClick=displayInfoDialog, onLongClickData=(app,))
        appPane.SKIP_CHILD_CHECK = True
        appIcon = pyos.GUI.Image((0, 0), surface=app.getIcon(), onClick=app.activate) #Long click uninstall
        appName = pyos.GUI.Text((0, 0), app.title, state.getColorPalette().getColor("item"), 12,
                                onClick=app.activate, onLongClick=uninstallAsk, onLongClickData=(app,))
        appIcon.position[0] = pyos.GUI.getCenteredCoordinates(appIcon, appPane)[0]
        appName.position[0] = pyos.GUI.getCenteredCoordinates(appName, appPane)[0]
        appIcon.position[1] = pyos.GUI.getCenteredCoordinates(appIcon, appPane)[1] - appName.height + 2
        appName.position[1] = appIcon.position[1] + appIcon.height
        appPane.addChild(appIcon)
        appPane.addChild(appName)
        pagedContainer.addChild(appPane)
    application.ui.addChild(pagedContainer)
    pagedContainer.goToPage()
    