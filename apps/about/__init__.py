import pyos

def onStart(s, a):
    tmapp = s.getApplicationList().getApp("task-manager")
    text = pyos.GUI.MultiLineText((0, 0), """Python OS 6.
Designed and programmed by Adam Furman.

Report bugs on GitHub at furmada/PythonOS

Contact the developer: furmada@gmail.com
    """, s.getColorPalette().getColor("item"), 14, width=a.ui.width, height=a.ui.height-40)
    btn = pyos.GUI.Button((0, a.ui.height-40), "Start Task Manager", s.getColorPalette().getColor("item"),
                          s.getColorPalette().getColor("background"), width=a.ui.width, height=40,
                          onClick=tmapp.activate)
    a.ui.addChild(text)
    a.ui.addChild(btn)
