import pyos

application = None

def getVisibleAppList():
    visible = []
    for app in state.getApplicationList().getApplicationList():
        if app.getIcon() != False:
            visible.append(app)
    return visible

def loadApps(pstate, app):
    global application, state
    state = pstate
    application = state.getActiveApplication()
    application.ui.backgroundColor = state.getColorPalette().getColor("background")
    pagedContainer = pyos.GUI.GriddedPagedContainer((0, 0), width=application.ui.width, height=application.ui.height, color=state.getColorPalette().getColor("background"),)
    for app in getVisibleAppList():
        appPane = pyos.GUI.Container((0, 0), transparent=True, width=pagedContainer.perColumn, height=pagedContainer.perRow, onClick=app.activate)
        appIcon = pyos.GUI.Image((0, 0), surface=app.getIcon(), onClick=app.activate) #Long click uninstall
        appName = pyos.GUI.Text((0, appIcon.height+2), app.title, state.getColorPalette().getColor("item"), 12, onClick=app.activate)
        appIcon.position[0] = pyos.GUI.getCenteredCoordinates(appIcon, appPane)[0]
        appName.position[0] = pyos.GUI.getCenteredCoordinates(appName, appPane)[0]
        appPane.addChild(appIcon)
        appPane.addChild(appName)
        pagedContainer.addChild(appPane)
    application.ui.addChild(pagedContainer)
    pagedContainer.goToPage()
    
def run():
    pass