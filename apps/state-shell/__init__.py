import pyos

app = None
state = None

def onStart(s, a):
    global app, state
    app = a
    state = s
    commandPrompt = pyos.GUI.TextEntryField((0, 0), width=app.ui.width, height=20, color=state.getColorPalette().getColor("item"), textColor=state.getColorPalette().getColor("background"))
    app.ui.addChild(commandPrompt)
    
def run():
    pass