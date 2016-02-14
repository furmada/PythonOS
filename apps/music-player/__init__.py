import pyos

def onStart(s, a):
    global state, app, player
    state = s
    app = a
    pyos.pygame.mixer.init()
    player = MusicPlayer()
    
class MusicPlayer(object):
    def __init__(self, playlist=[]):
        self.playlist = []
        self.currentlyPlaying = -1
        self.currentSongLength = 0
        self.elapsed = 0
        self.lastSkip = 0
        self.playing = False
        self.autoContinue = True
        self.screens = pyos.GUI.PagedContainer((0, 0), width=app.ui.width, height=app.ui.height-20, color=(245, 193, 110))
        self.generateSongScreen()
        self.generatePlaylistScreen()
        self.volumeSlider = pyos.GUI.Slider((20, app.ui.height-20), int(pyos.pygame.mixer_music.get_volume()*100), width=app.ui.width-20, height=20, backgroundColor=(245, 193, 110), 
                                            onChange=self.setVolume)
        app.ui.addChild(self.screens)
        app.ui.addChild(self.volumeSlider)
        app.ui.addChild(pyos.GUI.Image((0, app.ui.height-20), path="apps/music-player/volume.png", width=20, height=20))
        app.ui.backgroundColor = (245, 193, 110)
        self.screens.goToPage()
        if app.file != None:
            self.addToPlaylist(app.file)
            self.loadSong(app.file)
        
    def playPause(self):
        if len(self.playlist) == 0: return
        if self.playing:
            self.playing = False
            self.autoContinue = False
            self.playPauseBtn.setImage(path="apps/music-player/play.png")
            pyos.pygame.mixer_music.pause()
            return
        else:
            self.playPauseBtn.setImage(path="apps/music-player/pause.png")
            pyos.pygame.mixer_music.unpause()
            self.playing = True
            self.autoContinue = True
            
    def stop(self):
        pyos.pygame.mixer_music.stop()
        self.playPauseBtn.setImage(path="apps/music-player/play.png")
        self.playing = False
        self.elapsed = 0
        self.seeker.setPercent(0)
        self.autoContinue = False
        
    def loadSong(self, path):
        self.screens.goToPage()
        self.currentlyPlaying = self.playlist.index(path)
        pyos.pygame.mixer_music.load(path)
        self.titleText.setText(path[path.rfind("/")+1:])
        self.playPauseBtn.setImage(path="apps/music-player/pause.png")
        self.currentSongLength = self.getCurrentSongLength()
        pyos.pygame.mixer_music.play()
        self.playing = True
        self.autoContinue = True
        self.elapsed = 0
        self.lastSkip = 0
        
    def getCurrentSongLength(self):
        snd = pyos.pygame.mixer.Sound(self.playlist[self.currentlyPlaying])
        return snd.get_length()
        
    def seekSong(self, percent):
        try:
            pyos.pygame.mixer_music.rewind()
            pyos.pygame.mixer_music.play(0, self.currentSongLength * (percent / 100.0))
            self.lastSkip = int(self.currentSongLength * (percent / 100.0))
            if not self.playing:
                pyos.pygame.mixer_music.pause()
        except:
            if self.currentlyPlaying != -1:
                pyos.GUI.WarningDialog("Seeking is not supported in this file format.").display()
        
    def setVolume(self, percent):
        pyos.pygame.mixer_music.set_volume((percent / 100.0))
        
    def playlistSelection(self):
        state.getApplicationList().getApp("files").getModule().FilePicker((10, 10), app, width=app.ui.width-20, height=app.ui.height-20,
                                                                          onSelect=self.addToPlaylist).display()
        
    def addToPlaylist(self, song):
        self.playlist.append(song)
        if len(self.playlist) == 1:
            self.loadSong(song)
        self.populatePlaylistScroller()
        
    def removeFromList(self, song):
        if song == self.playlist[self.currentlyPlaying]:
            self.stop()
            self.currentlyPlaying = -1
            self.titleText.setText("No Song")
        self.playlist.remove(song)
        self.populatePlaylistScroller()
        
        
    def populatePlaylistScroller(self):
        self.playlistScroller.clearChildren()
        for song in self.playlist:
            cont = pyos.GUI.Container((0, 0), transparent=True, width=self.playlistScroller.container.width, height=40, border=1, borderColor=state.getColorPalette().getColor("item"),
                                      onClick=self.loadSong, onClickData=(song,))
            title = pyos.GUI.Text((2, 8), song[song.rfind("/")+1:], state.getColorPalette().getColor("item"), 24, onClick=self.loadSong, onClickData=(song,))
            rmbtn = pyos.GUI.Image((cont.width-40, 0), path="apps/music-player/remove.png", onClick=self.removeFromList, onClickData=(song,))
            cont.addChild(title)
            cont.addChild(rmbtn)
            self.playlistScroller.addChild(cont)
        
    def generatePlaylistScreen(self):
        self.playlistScreen = self.screens.generatePage()
        self.playlistScreen.backgroundColor = (245, 193, 110)
        title = pyos.GUI.Text((2, 8), "Playlist", state.getColorPalette().getColor("item"), 24)
        addBtn = pyos.GUI.Image((self.playlistScreen.width-40, 0), path="apps/music-player/add.png",
                                onClick=self.playlistSelection)
        self.playlistScreen.addChild(title)
        self.playlistScreen.addChild(addBtn)
        self.playlistScroller = pyos.GUI.ListScrollableContainer((0, 40), width=self.playlistScreen.width, height=self.playlistScreen.height-40, scrollAmount=40, color=(245, 193, 110))
        self.playlistScreen.addChild(self.playlistScroller)
        self.populatePlaylistScroller()
        self.screens.addPage(self.playlistScreen)
        
    def generateSongScreen(self):
        self.songScreen = self.screens.generatePage()
        self.songScreen.backgroundColor = (245, 193, 110)
        self.titleText = pyos.GUI.Text((2, 10), "No Song", state.getColorPalette().getColor("item"), 30)
        self.playPauseBtn = pyos.GUI.Image((0, self.songScreen.height-40), path="apps/music-player/play.png", onClick=self.playPause)
        self.stopBtn = pyos.GUI.Image((self.songScreen.width-40, self.songScreen.height-40), path="apps/music-player/stop.png", onClick=self.stop)
        self.seeker = pyos.GUI.Slider((40, self.songScreen.height-40), 0, width=self.songScreen.width-80, height=40, backgroundColor=(245, 193, 110),
                                      onChange=self.seekSong)
        self.songScreen.addChild(self.titleText)
        self.songScreen.addChild(self.playPauseBtn)
        self.songScreen.addChild(self.stopBtn)
        self.songScreen.addChild(self.seeker)
        self.screens.addPage(self.songScreen)
        
    def update(self):
        if not pyos.pygame.mixer_music.get_busy() and self.autoContinue:
            if self.currentlyPlaying + 1 < len(self.playlist):
                self.currentlyPlaying += 1
                self.loadSong(self.playlist[self.currentlyPlaying])
            else:
                self.stop()
            return
        if self.currentSongLength > 0 and self.playing:
            self.elapsed = (pyos.pygame.mixer_music.get_pos() / 1000)
            self.seeker.setPercent(((self.elapsed + self.lastSkip) / self.currentSongLength)*100)
        
def run():
    player.update()