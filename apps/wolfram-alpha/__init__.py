import pyos
import tungsten
from urllib import urlretrieve

def onStart(s, a):
    global state, app, client, waApp
    state = s
    app = a
    client = tungsten.Tungsten("77QKHJ-R6QEKHE4YA")
    waApp = WolframAlpha()
    
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

def open_picture(pic):
    img_viewer = state.getApplicationList().getApp("image-viewer")
    img_viewer.file = "temp/wa_img"+str(pic)+".gif"
    img_viewer.activate()
    
def query(search, pages):
    resp = client.query(search)
    title = None
    pages.clearChildren()
    if not resp.success:
        errPage = pages.generatePage()
        errTxt = pyos.GUI.Text((0, 0), "Error", state.getColorPalette().getColor("error"), 18)
        errDesc = pyos.GUI.Text((0, 20), str(resp.error), state.getColorPalette().getColor("item"), 18)
        errPage.addChild(errTxt)
        errPage.addChild(errDesc)
        pages.addPage(errPage)
        pages.removePage(0)
        pages.goToPage()
        return pages
    p = 0
    for pod in resp.pods:
        container = pages.generatePage()
        title = pyos.GUI.Text((2, 0), pod.title, state.getColorPalette().getColor("item"), 18)
        has_img = "img" in pod.format.keys()
        has_text = "plaintext" in pod.format.keys() and pod.format["plaintext"][0] != None
        if has_img and has_text:
            urlretrieve(pod.format["img"][0]["url"], "temp/wa_img"+str(p)+".gif")
            loaded = pyos.pygame.image.load("temp/wa_img"+str(p)+".gif")
            scaled = aspect_scale(loaded, (container.width, (container.height-20)/2))
            img = pyos.GUI.Image((0, 20), surface=scaled, border=2, borderColor=state.getColorPalette().getColor("accent"),
                                 onClick=open_picture, onClickData=(p,))
            th = container.height - img.height - 20
            text = pyos.GUI.ExpandingMultiLineText((0, 0), pod.format["plaintext"][0] if has_text and pod.format["plaintext"][0] != None else pod.format["img"][0]["alt"], state.getColorPalette().getColor("item"), 16,
                                          width=container.width, height=th)
            text_holder = pyos.GUI.TextScrollableContainer((0, container.height-th), text, width=container.width, height=th)
            container.addChild(img)
            container.addChild(text_holder)
            container.addChild(title)
        if has_img and not has_text:
            urlretrieve(pod.format["img"][0]["url"], "temp/wa_img"+str(p)+".gif")
            loaded = pyos.pygame.image.load("temp/wa_img"+str(p)+".gif")
            scaled = aspect_scale(loaded, (container.width, (container.height-20)))
            img = pyos.GUI.Image((0, 20), surface=scaled, border=2, borderColor=state.getColorPalette().getColor("accent"),
                                 onClick=open_picture, onClickData=(p,))
            container.addChild(img)
            container.addChild(title)
        if has_text and not has_img:
            text = pyos.GUI.ExpandingMultiLineText((0, 20), pod.format["plaintext"][0] if has_text and pod.format["plaintext"][0] != None else pod.format["img"][0]["alt"], state.getColorPalette().getColor("item"), 16,
                                          width=container.width, height=container.height-20)
            text_holder = pyos.GUI.TextScrollableContainer((0, container.height-th), text, width=container.width, height=th)
            container.addChild(text_holder)
            container.addChild(title)
        p += 1
        pages.addPage(container)
    if len(resp.pods) == 0:
        errPage = pages.generatePage()
        errTxt = pyos.GUI.Text((2, 0), "No Results for Query", state.getColorPalette().getColor("error"), 18)
        errDesc = pyos.GUI.Text((2, 20), "Try different search parameters.", state.getColorPalette().getColor("item"), 18)
        errPage.addChild(errTxt)
        errPage.addChild(errDesc)
        pages.addPage(errPage)
    pages.removePage(0)
    pages.goToPage()
    return pages

class WolframAlpha(object):
    def __init__(self):
        self.querybar = pyos.GUI.TextEntryField((0, 0), width=app.ui.width-40, height=20, color=state.getColorPalette().getColor("item"), textColor=state.getColorPalette().getColor("background"))
        self.pages = pyos.GUI.PagedContainer((0, 20), width=app.ui.width, height=app.ui.height-20)
        self.gobtn = pyos.GUI.Button((app.ui.width-40, 0), "Go", state.getColorPalette().getColor("item"), state.getColorPalette().getColor("background"), 16,
                                     onClick=self.query, width=40, height=20)
        self.pages.clearChildren()
        app.ui.addChild(self.querybar)
        app.ui.addChild(self.pages)
        app.ui.addChild(self.gobtn)
    
    def query(self):
        state.getGUI().displayStandbyText("Searching...")
        query(self.querybar.getText(), self.pages)
        