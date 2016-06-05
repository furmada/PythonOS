import pyos

def onStart(s, a):
    global state, app
    state = s
    app = a
    app.ui.clearChildren()
    Gallery()
    
def aspect_scale(img, (bx, by)):
    ix,iy = img.get_size()
    if ix > iy:
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pyos.pygame.transform.scale(img, (int(sx), int(sy)))
    
class GalleryThumbnail(pyos.GUI.Container):
    def __init__(self, position, w, h, image, imageLoadApp):
        self.imageLoadApp = imageLoadApp
        self.image = image
        super(GalleryThumbnail, self).__init__(position, width=w, height=h, color=state.getColorPalette().getColor("background"),
                                               border=2, borderColor=(200, 200, 200),
                                               onClick=self.open)
        self.SKIP_CHILD_CHECK = True
        self.picture = pyos.GUI.Image(((self.width/2)-20, ((self.height-20)/2)-20), path="apps/gallery/loading.png")
        self.title = pyos.GUI.Text((2, self.height-19), self.image.replace("\\", "/")[self.image.replace("\\", "/").rfind("/")+1:],
                                   state.getColorPalette().getColor("item"), 16)
        loadTask = pyos.ParallelTask(self.loadRealImage)
        state.getThreadController().addThread(loadTask)
        self.addChild(self.picture)
        self.addChild(self.title)
        
    def open(self):
        self.imageLoadApp.file = self.image
        self.imageLoadApp.activate()
        
    def loadRealImage(self):
        img = aspect_scale(pyos.pygame.image.load(self.image), (self.width, self.height-20))
        self.picture.setImage(surface=img, resize=True)
        self.picture.position[0] = pyos.GUI.getCenteredCoordinates(self.picture, self)[0]
        self.picture.position[1] = ((self.height-20)/2)-(self.picture.height/2)
    
class Gallery(object):
    def __init__(self):
        self.filesApp = state.getApplicationList().getApp("files")
        self.imageViewerApp = state.getApplicationList().getApp("image-viewer")
        
        self.pages = pyos.GUI.GriddedPagedContainer((0, 40), 2, 2, width=app.ui.width, height=app.ui.height-40, color=state.getColorPalette().getColor("background"), margin=0, padding=0)
        self.titleText = pyos.GUI.Text((2, 6), "Gallery", state.getColorPalette().getColor("item"), 24)
        self.path = ""
        self.selectBtn = pyos.GUI.Image((app.ui.width-40, 0), surface=self.filesApp.getIcon(),
                                        onClick=self.selectDir)
        app.ui.addChild(self.pages)
        app.ui.addChild(self.titleText)
        app.ui.addChild(self.selectBtn)
        self.pages.addPage(self.pages.generatePage())
        self.pages.goToPage()
        
    def loadDir(self, path):
        if not pyos.os.path.exists(path): return
        self.path = path
        self.pages.clearChildren()
        self.titleText.setText(path[path.rfind("/")+1:])
        for path in [pyos.os.path.join(self.path, s) for s in pyos.os.listdir(self.path) if pyos.os.path.isfile(pyos.os.path.join(self.path, s))]:
            if path[path.rfind("."):].lower() not in [e.lower() for e in self.imageViewerApp.parameters["file"]]: continue
            self.pages.addChild(GalleryThumbnail((0, 0), self.pages.perColumn, self.pages.perRow, path, self.imageViewerApp))
        self.pages.goToPage()
        
    def selectDir(self):
        startDir = str(pyos.__file__).rstrip("pyos.pyc") if self.path=="" else self.path
        self.filesApp.getModule().FolderPicker((10, 10), width=app.ui.width-20, height=app.ui.height-20, startFolder=startDir,
                                   onSelect=self.loadDir).display()