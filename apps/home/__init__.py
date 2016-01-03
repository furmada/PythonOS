import pyos

app = None
state = None

def onLoad(s, a):
    global app, state
    app = a
    state = s
    welcomeText = pyos.GUI.Text((5, 5), "Welcome to Python OS 6.", state.getColorPalette().getColor("item"), 15)
    betaButton = pyos.GUI.Button((app.ui.width-100, app.ui.height-20), "Beta v1.0", state.getColorPalette().getColor("accent"), state.getColorPalette().getColor("item"),
                                 12, width=100, height=20, onClick=state.getApplicationList().getApp("state-shell").activate)
    app.ui.addChild(welcomeText)
    app.ui.addChild(betaButton)
    
def run():
    pass