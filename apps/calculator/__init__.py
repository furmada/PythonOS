import pyos
import math

ans = 0

def sqrt(n):
    return math.sqrt(n)

def nrt(r, n):
    return n**(1.0/r)

def onStart(s, a):
    global state, app
    state = s
    app = a
    calc = Calculator()
    
class Calculator(object):
    def __init__(self):
        app.ui.clearChildren()
        self.input = ""
        self.showingAns = False
        self.compField = pyos.GUI.Text((0, 20), "0", state.getColorPalette().getColor("item"), 40)
        self.ansField = pyos.GUI.Text((2, 2), "0", state.getColorPalette().getColor("item"), 16)
        
        l_paren = pyos.GUI.Button((40, 240), "(", state.getColorPalette().getColor("item"), state.getColorPalette().getColor("background"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=("(",),
                                          border=1, borderColor=(20,20,20))
        r_paren = pyos.GUI.Button((120, 240), ")", state.getColorPalette().getColor("item"), state.getColorPalette().getColor("background"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(")",),
                                          border=1, borderColor=(20,20,20))
        ansbtn = pyos.GUI.Button((80, 240), "ans", state.getColorPalette().getColor("item"), state.getColorPalette().getColor("background"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=("ans",),
                                          border=1, borderColor=(20,20,20))
        
        app.ui.addChild(l_paren)
        app.ui.addChild(r_paren)
        app.ui.addChild(ansbtn)
        
        app.ui.addChild(self.compField)
        app.ui.addChild(self.ansField)
        self.addNumBtns()
        self.addFunctionButtons()
        self.addSpecialButtons()
        
    def addInput(self, data):
        if self.input == "0" or self.showingAns:
            if data == "+" or data == "-" or data == "*" or data == "/" or data == "**":
                data = "ans" + data
            self.input = str(data)
            if self.showingAns:
                self.showingAns = False
                self.ansField.text = str(self.compField.text)
                self.ansField.refresh()
        else:
            self.input += str(data)
        self.compField.text = str(self.input)
        self.compField.refresh()
        
    def bkspcInput(self):
        if len(self.input) > 0:
            self.input = self.input[:len(self.input)-1]
        self.compField.text = str(self.input)
        self.compField.refresh()
            
    def clearInput(self):
        self.input = "0"
        self.compField.text = str(self.input)
        self.compField.refresh()
        
    def evaluate(self):
        try:
            curr_ans = self.ansField.text
            bestans = curr_ans
            if self.ansField.text.find(".") != -1:
                bestans = float(curr_ans)
            else:
                bestans = int(curr_ans)
            self.compField.text = eval(self.input, {"sqrt": sqrt, "nrt": nrt, "ans": bestans, "pi": math.pi})
        except:
            self.compField.text = "err"
        self.showingAns = True
        self.compField.refresh()
        
    def addNumBtns(self):
        self.numBtns = []
        self.numBtns.append(pyos.GUI.Button((40, 80), "7", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(7,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((80, 80), "8", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(8,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((120, 80), "9", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(9,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((40, 120), "4", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(4,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((80, 120), "5", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(5,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((120, 120), "6", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(6,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((40, 160), "1", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(1,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((80, 160), "2", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(2,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((120, 160), "3", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(3,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((80, 200), "0", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(0,),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((40, 200), ",", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(",",),
                                          border=1, borderColor=(200,200,200)))
        self.numBtns.append(pyos.GUI.Button((120, 200), ".", state.getColorPalette().getColor("background"), state.getColorPalette().getColor("item"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=(".",),
                                          border=1, borderColor=(200,200,200)))
        for nb in self.numBtns:
            app.ui.addChild(nb)
            
    def addFunctionButtons(self):
        self.fncBtns = []
        self.fncBtns.append(pyos.GUI.Button((160, 80), "+", (123, 209, 237), (20, 20, 20), 24,
                                          width=80, height=40, onClick=self.addInput, onClickData=("+",)))
        self.fncBtns.append(pyos.GUI.Button((160, 120), "-", (113, 199, 227), (20, 20, 20), 24,
                                          width=80, height=40, onClick=self.addInput, onClickData=("-",)))
        self.fncBtns.append(pyos.GUI.Button((160, 160), "x", (103, 189, 217), (20, 20, 20), 24,
                                          width=80, height=40, onClick=self.addInput, onClickData=("*",)))
        self.fncBtns.append(pyos.GUI.Button((160, 200), "/", (93, 179, 207), (20, 20, 20), 24,
                                          width=80, height=40, onClick=self.addInput, onClickData=("/",)))
        self.fncBtns.append(pyos.GUI.Button((160, 240), "=", (255, 198, 74), (20, 20, 20), 24,
                                          width=80, height=40, onClick=self.evaluate))
        for fb in self.fncBtns:
            app.ui.addChild(fb)
            
    def addSpecialButtons(self):
        self.spclBtns = []
        self.spclBtns.append(pyos.GUI.Button((0, 80), "del", state.getColorPalette().getColor("item"), state.getColorPalette().getColor("background"), 24,
                                          width=40, height=40, onClick=self.bkspcInput, onLongClick=self.clearInput))
        self.spclBtns.append(pyos.GUI.Button((0, 120), "^", (123, 209, 237), (20, 20, 20), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=("**",)))
        self.spclBtns.append(pyos.GUI.Button((0, 160), "sqrt", (113, 199, 227), (20, 20, 20), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=("sqrt(",)))
        self.spclBtns.append(pyos.GUI.Button((0, 200), "nrt", (103, 189, 217), (20, 20, 20), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=("nrt(",)))
        self.spclBtns.append(pyos.GUI.Button((0, 240), "pi", state.getColorPalette().getColor("item"), state.getColorPalette().getColor("background"), 24,
                                          width=40, height=40, onClick=self.addInput, onClickData=("pi",)))
        for sb in self.spclBtns:
            app.ui.addChild(sb)
            