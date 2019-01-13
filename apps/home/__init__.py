import pyos
from base64 import b16encode

app = None
state = None

def onLoad(s, a):
    global app, state
    app = a
    state = s
    welcomeText = pyos.GUI.Text((5, 5), "Welcome to Python OS 6.", state.getColorPalette().getColor("item"), 15)
    tutorialText = pyos.GUI.Text((5, 20), "Tap the rectangles for your apps.", state.getColorPalette().getColor("item"), 15)
    app.ui.addChild(welcomeText)
    app.ui.addChild(tutorialText)
    
def onUnload():
    state.getFunctionBar().container.backgroundColor = state.getColorPalette().getColor("background")
    state.getFunctionBar().clock_text.color = state.getColorPalette().getColor("accent")
    state.getFunctionBar().app_title_text.color = state.getColorPalette().getColor("item")
    state.getFunctionBar().app_title_text.refresh()
    state.getFunctionBar().clock_text.refresh()
    
def run():
    time = pyos.datetime.now()
    timetuple = (3*time.hour, 3*time.minute, 4.25*time.second)
    inverse = (255-timetuple[0], 255-timetuple[1], 255-timetuple[2])
    state.getFunctionBar().container.backgroundColor = timetuple
    state.getFunctionBar().app_title_text.color = inverse
    state.getFunctionBar().clock_text.color = inverse
    state.getFunctionBar().app_title_text.refresh()
    state.getFunctionBar().clock_text.refresh()
