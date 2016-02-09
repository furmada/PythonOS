import pyos
import datetime

def onStart(s, a):
    global state, application, timeText, secText, dateText, twelveHRTime
    state = s
    application = a
    
    twelveHRTime = False
    
    application.ui.backgroundColor = (53, 106, 166)
    timeText = pyos.GUI.Text((0, 40), datetime.datetime.now().strftime("%H:%M"), (220, 220, 220), 80,
                             onClick=switchTimeMode)
    secText = pyos.GUI.Text((0, 160), str(datetime.datetime.now().second), (220, 220, 220), 40)
    dateText = pyos.GUI.Text((0, application.ui.height-30), datetime.datetime.now().strftime("%A, %b %d"), (220, 220, 220), 20)
    timeText.position[0] = pyos.GUI.getCenteredCoordinates(timeText, application.ui)[0]
    secText.position[0] = pyos.GUI.getCenteredCoordinates(secText, application.ui)[0]
    dateText.position[0] = pyos.GUI.getCenteredCoordinates(dateText, application.ui)[0]
    
    application.ui.addChild(timeText)
    application.ui.addChild(secText)
    application.ui.addChild(dateText)
    
def switchTimeMode():
    global twelveHRTime
    twelveHRTime = not twelveHRTime
    
def run():
    if twelveHRTime:
        timeText.text = datetime.datetime.now().strftime("%I:%M")
    else:
        timeText.text = datetime.datetime.now().strftime("%H:%M")
    secText.text = str(datetime.datetime.now().second)
    dateText.text = datetime.datetime.now().strftime("%A, %b %d")
    timeText.position[0] = pyos.GUI.getCenteredCoordinates(timeText, application.ui)[0]
    secText.position[0] = pyos.GUI.getCenteredCoordinates(secText, application.ui)[0]
    dateText.position[0] = pyos.GUI.getCenteredCoordinates(dateText, application.ui)[0]
    application.ui.refresh()
    
def onResume():
    application.ui.backgroundColor = (53, 106, 166)