import pyos, datetime

def onStart(s, a):
    global state, app, watch
    state = s
    app = a
    watch = Stopwatch()
    
def onResume():
    app.ui.backgroundColor = (53, 106, 166)
    
class Lap(pyos.GUI.Container):
    def __init__(self, watch, mins, secs, hundredths):
        super(Lap, self).__init__((0, 0), color=state.getColorPalette().getColor("background"), border=1, borderColor=(200,200,200),
                                  width=watch.lapContainer.container.width, height=40)
        self.timetext = pyos.GUI.Text((2, 8), str(mins).rjust(2, "0")+":"+str(secs).rjust(2, "0")+"."+str(hundredths)[:2], state.getColorPalette().getColor("item"), 24)
        self.removeBtn = pyos.GUI.Image((self.width-40, 0), surface=state.getIcons().getLoadedIcon("delete"),
                                        onClick=watch.lapContainer.removeChild, onClickData=(self,))
        self.addChild(self.timetext)
        self.addChild(self.removeBtn)
    
class Stopwatch(object):
    def __init__(self):
        self.started = False
        self.time_text = pyos.GUI.Text((0, 0), "00:00.00", state.getColorPalette().getColor("item"), 60)
        self.time_text.position[0] = pyos.GUI.getCenteredCoordinates(self.time_text, app.ui)[0]
        self.startBtn = pyos.GUI.Button((0, 80), "Start", (200, 255, 200), (20, 20, 20), width=(app.ui.width/2-30), height=60,
                                        onClick=self.start)
        self.stopBtn = pyos.GUI.Button((app.ui.width-(app.ui.width/2-30), 80), "Stop", (255, 200, 200), (20, 20, 20), width=(app.ui.width/2-30), height=60,
                                       onClick=self.stop)
        self.lapBtn = pyos.GUI.Button((app.ui.width/2-30, 80), "Lap", (200, 200, 200), (20, 20, 20), width=60, height=60,
                                      onClick=self.lap)
        self.lapContainer = pyos.GUI.ListScrollableContainer((0, 140), color=state.getColorPalette().getColor("background"), width=app.ui.width,
                                                             height=app.ui.height-140, scrollAmount=40)
        self.startTime = None
        app.ui.backgroundColor = (53, 106, 166)
        
        app.ui.addChild(self.time_text)
        app.ui.addChild(self.startBtn)
        app.ui.addChild(self.stopBtn)
        app.ui.addChild(self.lapBtn)
        app.ui.addChild(self.lapContainer)
        
    def start(self):
        if self.started:
            self.startBtn.setText("Resume")
            self.started = False
            self.pauseTime = datetime.datetime.now()
        else:
            if self.time_text.text == "00:00.00":
                self.startTime = datetime.datetime.now()
            else:
                self.startTime = datetime.datetime.now() - (self.pauseTime - self.startTime)
            self.started = True
            self.startBtn.setText("Pause")
        self.startBtn.refresh()
        
    def stop(self):
        self.started = False
        self.time_text.text = "00:00.00"
        self.time_text.refresh()
        self.startBtn.setText("Start")
        
    def lap(self):
        if not self.started: return
        timed = datetime.datetime.now() - self.startTime
        lap = Lap(self, timed.seconds/60, timed.seconds%60, timed.microseconds % 1000000)
        self.lapContainer.addChild(lap)
        
    def update(self):
        if not self.started: return
        timed = datetime.datetime.now() - self.startTime
        self.time_text.text = str(timed.seconds/60).rjust(2, "0")+":"+str(timed.seconds%60).rjust(2, "0")+"."+str(timed.microseconds % 1000000)[:2]
        self.time_text.refresh()
        
def run():
    watch.update()
