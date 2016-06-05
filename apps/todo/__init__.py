import pyos

def onStart(s, a):
    global state, app, tdapp
    state = s
    app = a
    tdapp = TodoApp()
    load_todos()
    
def load_todos():
    global todos
    todos = app.dataStore.get("todos", [])
    tdapp.loadTodos()
    
def save_todos():
    app.dataStore["todos"] = todos
    tdapp.loadTodos()

class Todo(pyos.GUI.Overlay):
    def __init__(self, tdstate):
        self.tdstate = tdstate
        super(Todo, self).__init__((0, 40), width=app.ui.width, height=200)
        self.container.border = 2
        self.container.borderColor = state.getColorPalette().getColor("accent")
        self.title = pyos.GUI.Text((2, 2), "List Entry", state.getColorPalette().getColor("item"), 16)
        self.textField = pyos.GUI.MultiLineTextEntryField((2, 20), tdstate.get("text", ""), width=self.width-4, height=self.height-60, size=14, maxLines=3)
        self.saveBtn = pyos.GUI.Button((0, self.height-40), "Save", state.getColorPalette().getColor("accent"),
                                       state.getColorPalette().getColor("item"), 16, width=self.width/2, height=40,
                                       onClick=self.save)
        self.cancelBtn = pyos.GUI.Button((self.width/2, self.height-40), "Cancel", state.getColorPalette().getColor("item"),
                                       state.getColorPalette().getColor("background"), 16, width=self.width/2, height=40,
                                       onClick=self.hide)
        self.container.addChild(self.title)
        self.container.addChild(self.textField)
        self.container.addChild(self.saveBtn)
        self.container.addChild(self.cancelBtn)
        
    def save(self):
        global todos
        self.tdstate["text"] = self.textField.getText()
        if self.tdstate.get("checked", None) == None:
            self.tdstate["checked"] = False
        if self.tdstate.get("id", -1) == -1:
            self.tdstate["id"] = max([t["id"] for t in todos] + [-1]) + 1
            todos.append(self.tdstate)
        save_todos()
        self.hide()
        
def deleteTodo(tdstate, resp):
    global todos
    if resp != "Yes": return
    todos.remove(tdstate)
    save_todos()
    
def newTodo():
    td = Todo({})
    td.display()
    
def deleteAsk(tds):
    pyos.GUI.YNDialog("Delete?", "Really delete this todo item?", deleteTodo, (tds,)).display()
    
def saveCheckState(tds, box):
    global todos
    todos[todos.index(tds)]["checked"] = box.getChecked()
    save_todos()
        
def genTodoContainer(tdstate):
    tdo = Todo(tdstate)
    bgc = state.getColorPalette().getColor("background")
    if tdstate["checked"]:
        bgc = [c-20 for c in bgc]
    cont = pyos.GUI.Container((0, 0), width=tdapp.scroller.container.width, height=56, color=bgc,
                              border=1)
    text = pyos.GUI.MultiLineText((40, 0), tdstate["text"], state.getColorPalette().getColor("item"), 14, width=cont.width-80, height=cont.height,
                                  onClick=tdo.display)
    delbtn = pyos.GUI.Image((cont.width-40, 8), surface=state.getIcons().getLoadedIcon("delete"),
                            onClick=deleteAsk, onClickData=(tdstate,))
    box = pyos.GUI.Checkbox((4, 12), tdstate["checked"], width=32, height=32)
    box.setOnClick(saveCheckState, (tdstate, box))
    cont.addChild(text)
    cont.addChild(delbtn)
    cont.addChild(box)
    return cont

def genAddContainer():
    cont = pyos.GUI.Container((0, 0), width=tdapp.scroller.container.width, height=56, backgroundColor=state.getColorPalette().getColor("background"))
    text = pyos.GUI.Text((0, 0), "+ Add New", state.getColorPalette().getColor("accent"),
                         onClick=newTodo)
    text.setPosition(pyos.GUI.getCenteredCoordinates(text, cont))
    cont.addChild(text)
    return cont
    
class TodoApp(object):
    def __init__(self):
        self.scroller = pyos.GUI.ListScrollableContainer((0, 0), width=app.ui.width, height=app.ui.height, 
                                                         backgroundColor=state.getColorPalette().getColor("background"), scrollAmount=56)
        app.ui.addChild(self.scroller)
        
    def loadTodos(self):
        self.scroller.clearChildren()
        for tds in todos:
            self.scroller.addChild(genTodoContainer(tds))
        self.scroller.addChild(genAddContainer())