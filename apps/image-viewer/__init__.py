import pyos

def loadImage(path):
    img = None
    try:
        img = pyos.pygame.image.load(path)
    except:
        pyos.GUI.ErrorDialog("Cannot load image.").display()
        return
    app.ui.clearChildren()
    if img.get_width() > img.get_height():
        img = pyos.pygame.transform.rotate(img, 90)
    if img.get_width() > app.ui.width:
        ix, iy = img.get_size()
        scale_factor = app.ui.height/float(iy)
        sx = scale_factor * ix
        if sx > app.ui.width:
            scale_factor = app.ui.width/float(ix)
            sx = app.ui.width
            sy = scale_factor * iy
        else:
            sy = app.ui.height
        img = pyos.pygame.transform.scale(img, (int(sx), int(sy)))
    image = pyos.GUI.Image((0, 0), surface=img)
    image.position = pyos.GUI.getCenteredCoordinates(image, app.ui)
    app.ui.addChild(image)

def onStart(s, a):
    global state, app
    state = s
    app = a
    if app.file != None:
        loadImage(app.file)
    else:
        state.getApplicationList().getApp("files").getModule().FilePicker((10, 10), app, width=app.ui.width-20, height=app.ui.height-20,
                                                                          onSelect=loadImage).display()