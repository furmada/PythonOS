import pyos

def onStart(s, a):
    text = pyos.GUI.MultiLineText((0, 0), """
Python OS 6 for Raspberry Pi Touchscreen.
Programmed by Adam Furman, furmada@gmail.com.
Designed for a RPi with a touchscreen display attached (such as Adafruit's 320x240 PiTFT.
    """, s.getColorPalette().getColor("item"), 14, width=a.ui.width, height=a.ui.height)
    a.ui.addChild(text)