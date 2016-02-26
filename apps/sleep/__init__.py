import pyos

sleeping = False

def toggle():
    global sleeping
    sleeping = not sleeping
    if sleeping:
        pyos.os.system("sh /home/pi/display_off.sh")
        btn.setText("Wake")
    else:
        pyos.os.system("sh /home/pi/display_on.sh")
        btn.setText("Sleep")
        

def onStart(s, a):
    global state, app, btn
    state = s
    app = a
    btn = pyos.GUI.Button((0, 0), "Sleep", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 40,
                          border=5, borderColor=state.getColorPalette().getColor("accent"),
                          width=app.ui.width, height=app.ui.height,
                          onClick=toggle)
    app.ui.addChild(btn)