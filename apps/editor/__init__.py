import pyos

def onStart(s, a):
    global state, app, editor
    state = s
    app = a
    editor = Editor()
    
def save():
    editor.save()
    
class Editor(object):
    def __init__(self):
        self.path = ""
        self.fobj = None
        
        self.saved = False
        
        self.textField = pyos.GUI.MultiLineTextEntryField((0, 0), width=app.ui.width, height=app.ui.height-40, border=0)
        self.fnText = pyos.GUI.Text((2, app.ui.height-32), "new file", pyos.DEFAULT, 16)
        self.openBtn = pyos.GUI.Image((app.ui.width-80, app.ui.height-40), surface=state.getIcons().getLoadedIcon("open"),
                                      onClick=self.openAsk)
        self.saveBtn = pyos.GUI.Image((app.ui.width-40, app.ui.height-40), surface=state.getIcons().getLoadedIcon("save"),
                                      onClick=self.save, onClickData=(True,))
        
        app.ui.addChildren(self.textField, self.fnText, self.openBtn, self.saveBtn)
        
        if app.file != None:
            self.open(app.file)
            app.file = None
        
    def setPath(self, path):
        self.path = path
        self.save(True)
        
    def save(self, btn=False):
        self.saved = btn
        if not self.saved: return
        if self.path == "":
            state.getApplicationList().getApp("files").getModule().SaveAs("Enter a name for the file. A common extension is .txt",
                                                                          onSelect=self.setPath).display()
        else:
            try:
                self.fobj = open(self.path, "w")
                self.fobj.write(self.textField.getText())
                self.fobj.close()
                self.unsaved = False
                self.fnText.setText(self.path[max(self.path.rfind("/"), self.path.rfind("\\"))+1:])
            except:
                pyos.GUI.ErrorDialog("The file "+self.path+" could not be written to.").display()
        
    def openAsk(self):
        state.getApplicationList().getApp("files").getModule().FilePicker(("5%", "5%"), app, width="90%", height="90%",
                                                                          onSelect=self.open).display()
    
    def open(self, path):
        self.path = path
        ro = open(self.path, "rU")
        self.textField.setText(str(unicode(ro.read(), errors="ignore")))
        ro.close()
        self.fnText.setText(path[max(path.rfind("/"), path.rfind("\\"))+1:])