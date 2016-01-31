import pyos
from base64 import b16encode

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
    t = 0
    while t < 10:
        state.getNotificationQueue().push(pyos.Notification("Welcome "+str(t), "Python OS 6 beta 1"))
        t += 1
    
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