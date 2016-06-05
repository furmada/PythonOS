import pyos

def shutdown(resp):
    if resp != "Yes":
        pyos.Application.fullCloseCurrent()
        return
    pyos.os.system("fbi -T 1 -a -noverbose /etc/splash0.png")
    pyos.os.system("sudo shutdown -h now")
    pyos.State.exit()
    
def sdAsk(*args):
    global state, app
    if len(args) > 0:
        state = args[0]
        app = args[1]
    pyos.GUI.YNDialog("Shut Down", "Are you sure you wish to shut down your device?", shutdown).display()