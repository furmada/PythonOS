import pyos
from math import sqrt

def onStart(s, a):
    global state, app, picasso
    state = s
    app = a
    picasso = Picasso()

class PainterCanvas(pyos.GUI.Canvas):
    def __init__(self, position, **data):
        self.layers = []
        self.paintPoints = []
        self.color = data.get("color", (0, 0, 0, 255))
        self.fillWidth = data.get("fillWidth", 0)
        self.mode = data.get("mode", "line")
        super(PainterCanvas, self).__init__(position, **data)
        self.internalClickOverrides["onClick"] = (self.paint, (True,))
        self.internalClickOverrides["onLongClick"] = (self.paint, (True,))
        self.internalClickOverrides["onIntermediateUpdate"] = (self.paint, ())
        self.addLayer()
        
    def _distance(self, pt0, pt1):
        return int(sqrt((pt0[0]-pt1[0])**2 + (pt0[1]-pt1[1])**2))
        
    def paint(self, end=False):
        self.paintPoints.append(self.innerClickCoordinates)
        if len(self.paintPoints) <= 1: 
            self.addLayer()
            return
        else:
            self.popLayer()
        self.addLayer()
        if self.mode == "line":
            pyos.pygame.draw.lines(self.layers[-1], self.color, False, self.paintPoints)
        if self.mode == "rect":
            pyos.pygame.draw.rect(self.layers[-1], self.color, [self.paintPoints[0][0], self.paintPoints[0][1],
                                                                self.paintPoints[-1][0] - self.paintPoints[0][0],
                                                                self.paintPoints[-1][1] - self.paintPoints[0][1]], self.fillWidth)
        if self.mode == "circle":
            pyos.pygame.draw.circle(self.layers[-1], self.color, self.paintPoints[0],
                                    self._distance(self.paintPoints[0], self.paintPoints[-1]), self.fillWidth)
        if self.mode == "ellipse":
            if self.paintPoints[-1][0] - self.paintPoints[0][0] >= 0 and self.paintPoints[-1][1] - self.paintPoints[0][1] >= 0:
                pyos.pygame.draw.ellipse(self.layers[-1], self.color, [self.paintPoints[0][0], self.paintPoints[0][1],
                                                                       self.paintPoints[-1][0] - self.paintPoints[0][0],
                                                                       self.paintPoints[-1][1] - self.paintPoints[0][1]], self.fillWidth)
            else:
                if self.paintPoints[-1][0] - self.paintPoints[0][0] < 0 and self.paintPoints[-1][1] - self.paintPoints[0][1] >= 0:
                    pyos.pygame.draw.ellipse(self.layers[-1], self.color, [self.paintPoints[0][0] + (self.paintPoints[-1][0] - self.paintPoints[0][0]),
                                                                           self.paintPoints[0][1],
                                                                           -(self.paintPoints[-1][0] - self.paintPoints[0][0]),
                                                                           self.paintPoints[-1][1] - self.paintPoints[0][1]], self.fillWidth)
                if self.paintPoints[-1][0] - self.paintPoints[0][0] >= 0 and self.paintPoints[-1][1] - self.paintPoints[0][1] < 0:
                    pyos.pygame.draw.ellipse(self.layers[-1], self.color, [self.paintPoints[0][0],
                                                                           self.paintPoints[0][1] + (self.paintPoints[-1][1] - self.paintPoints[0][1]),
                                                                           self.paintPoints[-1][0] - self.paintPoints[0][0],
                                                                           -(self.paintPoints[-1][1] - self.paintPoints[0][1])], self.fillWidth)
                if self.paintPoints[-1][0] - self.paintPoints[0][0] < 0 and self.paintPoints[-1][1] - self.paintPoints[0][1] < 0:
                    pyos.pygame.draw.ellipse(self.layers[-1], self.color, [self.paintPoints[0][0] + (self.paintPoints[-1][0] - self.paintPoints[0][0]),
                                                                           self.paintPoints[0][1] + (self.paintPoints[-1][1] - self.paintPoints[0][1]),
                                                                           -(self.paintPoints[-1][0] - self.paintPoints[0][0]),
                                                                           -(self.paintPoints[-1][1] - self.paintPoints[0][1])], self.fillWidth)
        if end: 
            self.paintPoints = []
    
    def setDimensions(self):
        super(PainterCanvas, self).setDimensions()
        for layer in self.layers:
            layer = pyos.pygame.transform.scale(layer, (self.computedWidth, self.computedHeight))
            
    def addLayer(self):
        self.layers.append(pyos.pygame.Surface((self.computedWidth, self.computedHeight), pyos.pygame.SRCALPHA))
        
    def popLayer(self):
        return self.layers.pop()
    
    def render(self, largerSurface):
        self.surface.fill((0, 0, 0, 0))
        for l in self.layers:
            self.surface.blit(l, (0, 0))
        super(PainterCanvas, self).render(largerSurface)
        
class Menu(pyos.GUI.Overlay):
    def __init__(self):
        hUnit = (app.ui.width / 100) * 20
        super(Menu, self).__init__(("80%", app.ui.height - (hUnit * 4)), width=hUnit, height=hUnit * 4, color=(255, 255, 255))
        self.container.border = 1
        self.clearBtn = pyos.GUI.Image((0, 0), surface=state.getIcons().getLoadedIcon("delete"), width=hUnit, height=hUnit,
                                       onClick=self.clear)
        self.saveBtn = pyos.GUI.Image((0, hUnit), surface=state.getIcons().getLoadedIcon("save"), width=hUnit, height=hUnit,
                                       onClick=self.save)
        self.addChild(self.clearBtn)
        self.addChild(self.saveBtn)
        
    def clear(self):
        picasso.clear()
        self.hide()
        
    def save(self):
        picasso.pickSaveFolder()
        self.hide()
        
class Picasso(object):
    def __init__(self):
        self.undo_history = []
        self.menu = Menu()
        self.canvas = PainterCanvas((0, 0), width="100%", height="90%")
        self.modesel = pyos.GUI.Selector((0, "90%"), ["Line", "Rectangle", "Circle", "Ellipse"],
                                         width="40%", height="10%", border=1, onValueChanged=self.setCanvasMode)
        self.undoBtn = pyos.GUI.Button(("40%", "90%"), "Undo", width="20%", height="10%", onClick=self.undo)
        self.redoBtn = pyos.GUI.Button(("60%", "90%"), "Redo", state.getColorPalette().getColor("lighter:background"),
                                       width="20%", height="10%", onClick=self.redo)
        self.menuBtn = pyos.GUI.Button(("80%", "90%"), "More", state.getColorPalette().getColor("lighter:accent"),
                                       width="20%", height="10%", onClick=self.menu.display)
        app.ui.addChildren(self.canvas, self.modesel, self.undoBtn, self.redoBtn, self.menuBtn)
    
    def undo(self):
        if len(self.canvas.layers) > 0: self.undo_history.append(self.canvas.popLayer())
        
    def redo(self):
        if len(self.undo_history) > 0: self.canvas.layers.append(self.undo_history.pop())
        
    def clear(self):
        self.undo_history = []
        self.canvas.layers = []
        
    def save(self, folder, filename):
        pyos.pygame.image.save(self.canvas.surface, pyos.os.path.join(folder, filename))
        pyos.GUI.OKDialog("Saved", "The file was successfully written").display()
        
    def promptSaveFile(self, folder):
        pyos.GUI.AskDialog("Save As", "Pick a name for your creation.", self.save, (folder,)).display()
        
    def pickSaveFolder(self):
        state.getApplicationList().getApp("files").getModule().FolderPicker(("10%", "10%"), width="80%", height="80%",
                                                                            onSelect=self.promptSaveFile, startFolder="docs").display()
        
    def setCanvasMode(self, selection):
        if selection == "Line": self.canvas.mode = "line"
        if selection == "Rectangle": self.canvas.mode = "rect"
        if selection == "Circle": self.canvas.mode = "circle"
        if selection == "Ellipse": self.canvas.mode = "ellipse"
        
        
    