import pyos

state = None
app = None

def loadFile(path):
    app.ui.clearChildren()
    f = open(path, "rU")
    lnCount = len(f.readlines())
    scroller = pyos.GUI.ScrollableContainer((0, 0), width=app.ui.width, height=app.ui.height, transparent=True)
    text = pyos.GUI.MultiLineText((0, 0), f.read(), state.getColorPalette().getColor("item"), width=scroller.container.width, height=16*lnCount)
    scroller.addChild(text)
    app.ui.addChild(scroller)
    app.ui.refresh()
    f.close()
    print "loaded file "+path
    print app.ui.childComponents[0].childComponents[0].childComponents

def onStart(s, a):
    global state, app
    state = s
    app = a
    