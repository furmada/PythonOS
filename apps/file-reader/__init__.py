import pyos

state = None
app = None

def loadFile(path):
    state.getGUI().displayStandbyText("Loading file")
    f = open(path, "rU")
    contents = str(f.read())
    scroller = pyos.GUI.TextScrollableContainer((0, 0), width=app.ui.width, height=app.ui.height)
    scroller.getTextComponent().setText(contents)
    app.ui.addChild(scroller)
    app.ui.refresh()
    f.close()

def onStart(s, a):
    global state, app
    state = s
    app = a
    if app.file != None:
        loadFile(app.file)
        app.file = None
    else:
        state.getApplicationList().getApp("files").getModule().FilePicker((10, 10), app, width=app.ui.width-20, height=app.ui.height-20,
                                                                          onSelect=loadFile).display()