import pyos

state = None
app = None

def lines(data):
    count = 1
    for c in data.replace("\r\n", '\n'):
        if c == '\n':
            count += 1
    return count

def loadFile(s, a, path):
    global state, app
    state = s
    app = a
    app.ui.clearChildren()
    app.ui.clearDialog()
    f = open(path, "rU")
    contents = str(f.read())
    lnCount = lines(contents)
    scroller = pyos.GUI.ScrollableContainer((0, 0), width=app.ui.width, height=app.ui.height)
    text = pyos.GUI.MultiLineText((0, 0), contents, (0, 0, 0), 12, width=scroller.container.width, height=16*lnCount)
    scroller.addChild(text)
    app.ui.addChild(scroller)
    app.ui.refresh()
    f.close()

def onStart(s, a):
    global state, app
    state = s
    app = a
    state.getApplicationList().getApp("files").getModule().LocationPicker(loadFile).display()