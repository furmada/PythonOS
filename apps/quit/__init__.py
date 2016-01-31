import pyos

state = None
app = None
def onLoad(s, a):
    global state, app
    state = s
    app = a
    app.ui.backgroundColor = (0, 0, 0, 0)
    dialog = pyos.GUI.YNDialog("Exit Python OS", "Are you sure you want to exit Python OS 6?\nThis will close all active applications and you may lose unsaved data.", parseResponse)
    dialog.display()
    app.ui.refresh()
    
def parseResponse(resp):
    if resp == "Yes":
        state.exit()
    pyos.Application.fullCloseCurrent()
    