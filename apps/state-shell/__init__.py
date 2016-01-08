import pyos

app = None
state = None
commandPrompt = None
output = None

def onStart(s, a):
    global app, state, commandPrompt, output
    app = a
    state = s
    commandPrompt = pyos.GUI.TextEntryField((0, 0), width=app.ui.width-25, height=25, color=state.getColorPalette().getColor("item"), textColor=state.getColorPalette().getColor("background"))
    goButton = pyos.GUI.Button((app.ui.width-23, 0), " -> ", state.getColorPalette().getColor("item"), state.getColorPalette().getColor("background"), 18, width=23, height=25, onClick=executeCommand)
    output = pyos.GUI.MultiLineText((0, 25), "Output will appear here", state.getColorPalette().getColor("item"), width=app.ui.width, height=app.ui.height-25)
    app.ui.addChild(commandPrompt)
    app.ui.addChild(goButton)
    app.ui.addChild(output)
    
def executeCommand():
    command = commandPrompt.getText()
    if command.startswith("."):
        command = "state" + command
    else:
        command = "state." + command
    try:
        returned = eval(command, {"state": state, "Static": pyos.State})
        output.text = str(returned)
        try:
            output.text += "\nObject Representation:\n"+str(returned.__dict__)
        except: pass
    except:
        output.text = "Error evaluating command."
    output.refresh()