import pyos, datetime

def onStart(s, a):
    global state, app, timer
    state = s
    app = a
    timer = Timer()
    
def onResume():
    app.ui.backgroundColor = (53, 106, 166)
    
class Timer(object):
    def __init__(self):
        self.minutes = 0
        self.seconds = 0
        self.started = False
        self.endDelta = None
        app.ui.backgroundColor = (53, 106, 166)
        self.min_text = pyos.GUI.Text((0, 40), "00m", state.getColorPalette().getColor("item"), 70)
        self.sec_text = pyos.GUI.Text((app.ui.width/2, 40), "00s", state.getColorPalette().getColor("item"), 70)
        self.min_inc = pyos.GUI.Button((0, 0), "+", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                        width=(app.ui.width/2)-2, height=40,
                                        onClick=self.changeMinutes, onClickData=(1,),
                                        onLongClick=self.changeMinutes, onLongClickData=(5,))
        self.sec_inc = pyos.GUI.Button(((app.ui.width/2)+2, 0), "+", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                        width=(app.ui.width/2)+2, height=40,
                                        onClick=self.changeSeconds, onClickData=(1,),
                                        onLongClick=self.changeSeconds, onLongClickData=(10,))
        self.min_dec = pyos.GUI.Button((0, 120), "-", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                        width=(app.ui.width/2)-2, height=40,
                                        onClick=self.changeMinutes, onClickData=(-1,),
                                        onLongClick=self.changeMinutes, onLongClickData=(-5,))
        self.sec_dec = pyos.GUI.Button(((app.ui.width/2)+2, 120), "-", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                        width=(app.ui.width/2)+2, height=40,
                                        onClick=self.changeSeconds, onClickData=(-1,),
                                        onLongClick=self.changeSeconds, onLongClickData=(-10,))
        self.startBtn = pyos.GUI.Button((0, app.ui.height-80), "Start", (200, 255, 200), (20, 20, 20), 20, width=app.ui.width/2, height=80,
                                        onClick=self.start)
        self.resetBtn = pyos.GUI.Button((app.ui.width/2, app.ui.height-80), "Reset", (255, 200, 200), (20, 20, 20), 20, width=app.ui.width/2, height=80,
                                        onClick=self.stop)
        
        app.ui.addChild(self.min_text)
        app.ui.addChild(self.sec_text)
        app.ui.addChild(self.min_inc)
        app.ui.addChild(self.min_dec)
        app.ui.addChild(self.sec_inc)
        app.ui.addChild(self.sec_dec)
        app.ui.addChild(self.startBtn)
        app.ui.addChild(self.resetBtn)
        
    def start(self):
        if self.started:
            self.startBtn.setText("Resume")
            self.started = False
        else:
            if self.sec_text.text == "00s" and self.min_text.text == "00m": return
            now = datetime.datetime.now()
            if self.startBtn.textComponent.text == "Resume":
                self.endDelta = now + datetime.timedelta(minutes=int(self.min_text.text.rstrip("m")), seconds=int(self.sec_text.text.rstrip("s")))
            else:
                self.endDelta = now + datetime.timedelta(minutes=self.minutes, seconds=self.seconds)
            self.startBtn.setText("Pause")
            self.started = True
        self.startBtn.refresh()
        
    def stop(self):
        self.started = False
        if self.seconds == 0 and self.minutes == 0:
            self.min_text.text = "00m"
            self.sec_text.text = "00s"
        else:
            self.min_text.text = str(self.minutes)+"m"
            self.sec_text.text = str(self.seconds)+"s"
        self.min_text.refresh()
        self.sec_text.refresh()
        self.startBtn.setText("Start")
        app.ui.backgroundColor = (53, 106, 166)
        
    def changeMinutes(self, how):
        if self.minutes + how < 0 or self.started: return
        self.minutes += how
        self.min_text.text = str(self.minutes)+"m"
        self.min_text.refresh()
        self.min_text.position[0] = (app.ui.width/2) - self.min_text.width
        
    def changeSeconds(self, how):
        if self.seconds + how < 0 or self.started: return
        self.seconds += how
        if self.seconds >= 60:
            self.changeMinutes(1)
            self.seconds -= 60
        self.sec_text.text = str(self.seconds)+"s"
        self.sec_text.refresh()
    
    def update(self):
        if not self.started: return
        timed = self.endDelta - datetime.datetime.now()
        if timed.total_seconds() <= 1:
            app.ui.backgroundColor = (240, 98, 108)
            self.min_text.text = "00m"
            self.sec_text.text = "00s"
            self.startBtn.setText("Start")
            self.started = False
        else:
            self.min_text.text = str(timed.seconds/60)+"m"
            self.sec_text.text = str(timed.seconds%60)+"s"
        self.min_text.refresh()
        self.sec_text.refresh()

def run():
    timer.update()