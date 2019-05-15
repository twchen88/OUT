# Menu - set up full screen menus with buttons
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from panda3d.core import *

# Modified from https://grimfang-studio.org/data/books/book1/Panda3D%20Book%201.pdf page 59

# start menu
class StartMenu:
    def __init__(self):
        self.frameMain = DirectFrame(frameSize = (base.a2dLeft, base.a2dRight,
                            base.a2dBottom, base.a2dTop), frameColor=(0,0,0,0))
        self.frameMain.setTransparency(1)
        # background image from https://www.shutterstock.com/it/video/clip-5477162-dark-scary-dungeon-high-definition
        self.frameBackground = DirectFrame(image = ('models/startmenutest.jpg'), sortOrder = (-1),
                frameSize = (base.a2dLeft, base.a2dRight, base.a2dBottom, base.a2dTop))
        self.frameBackground.reparentTo(render2d)
        
        self.title = DirectLabel(scale = 0.25, pos = (0.0, 0.0, base.a2dTop - 0.25),
                            frameColor = (0, 0, 0, 0), text="OUT", text_fg=(1,1,1,1))
        self.title.setTransparency(1)
        self.title.reparentTo(self.frameMain)
        self.btnStart = self.createButton("Start", 0.25, ["Menu-Start"])
        self.btnInstr = self.createButton('Instructions', -0.25, ['Menu-Instructions'])
        self.btnExit = self.createButton("Quit", -0.75, ["Menu-Quit"])
        
        self.hide()
    
    # create buttons
    def createButton(self, text,verticalPos, eventArgs):
        btn = DirectButton(text=text,scale=0.25, pos=(0,0,verticalPos), command=base.messenger.send,
                            extraArgs=eventArgs, rolloverSound=None, clickSound=None)
        btn.reparentTo(self.frameMain)

    def show(self):
        self.frameMain.show()
        self.frameBackground.show()

    def hide(self):
        self.frameMain.hide()
        self.frameBackground.hide()
        

# losing screen
class EndMenu:
    def __init__(self):
        self.frameMain = DirectFrame(frameSize = (base.a2dLeft, base.a2dRight,
                            base.a2dBottom, base.a2dTop), frameColor=(0,0,0,0))
        self.frameMain.setTransparency(1)
        
        self.title = DirectLabel(scale = 0.25, pos = (0.0, 0.0, base.a2dTop - 0.25),
                            frameColor = (0, 0, 0, 0), text="Unlucky...\nTry next time", text_fg=(1,1,1,1))
        self.title.setTransparency(1)
        self.title.reparentTo(self.frameMain)
        # background image taken from http://www.leagueittous.com/2015/03/12/sorry-you-lose/
        self.frameBackground = DirectFrame(image = ('models/game-over.png'), sortOrder = (-1),
                frameSize = (base.a2dLeft, base.a2dRight, base.a2dBottom, base.a2dTop))
        self.frameBackground.reparentTo(render2d)
        self.btnExit = self.createButton("Quit", -0.75, ["Menu-Quit"])
        self.hide()
    
    def createButton(self, text,verticalPos, eventArgs):
        btn = DirectButton(text=text,scale=0.25, pos=(0,0,verticalPos), command=base.messenger.send,
                            extraArgs=eventArgs, rolloverSound=None, clickSound=None)
        btn.reparentTo(self.frameMain)

    def show(self):
        self.frameMain.show()
        self.frameBackground.show()

    def hide(self):
        self.frameMain.hide()
        self.frameBackground.hide()

# instructions
class Instructions:
    def __init__(self):
        self.frameMain = DirectFrame(frameSize = (base.a2dLeft, base.a2dRight,
                            base.a2dBottom, base.a2dTop), frameColor=(0,0,0,0))
        self.frameMain.setTransparency(1)
        self.content = DirectLabel(scale = 0.1, pos = (0.0, 0.0, base.a2dTop - 0.25),
                            frameColor = (0, 0, 0, 0), text="Place hand above leap motion to control the sword.\nPress 'o' to open chest.\nPress space to open door to next level.\nUse WSAD to control motion.\nTurn left and right using Q and E.\n You can only enter the next level when you have \n killed more than 15 enemies. Good luck!", text_fg=(1,1,1,1))
        self.content.setTransparency(1)
        self.content.reparentTo(self.frameMain)
        self.btnStartGame = self.createButton("Start Game", -0.25, ["Instructions-startGame"])
        self.btnExit = self.createButton("Quit", -0.75, ["Menu-Quit"])
        # background image from https://www.shutterstock.com/it/video/clip-5477162-dark-scary-dungeon-high-definition
        self.frameBackground = DirectFrame(image = ('models/startmenutest.jpg'), sortOrder = (-1),
                frameSize = (base.a2dLeft, base.a2dRight, base.a2dBottom, base.a2dTop))
        self.frameBackground.reparentTo(render2d)
        self.hide()
    
    def createButton(self, text,verticalPos, eventArgs):
        btn = DirectButton(text=text,scale=0.25, pos=(0,0,verticalPos), command=base.messenger.send,
                            extraArgs=eventArgs, rolloverSound=None, clickSound=None)
        btn.reparentTo(self.frameMain)

    def show(self):
        self.frameMain.show()
        self.frameBackground.show()

    def hide(self):
        self.frameMain.hide()
        self.frameBackground.hide()

# winning screen
class Win:
    def __init__(self):
        self.frameMain = DirectFrame(frameSize = (base.a2dLeft, base.a2dRight,
                            base.a2dBottom, base.a2dTop), frameColor=(0,0,0,0))
        self.frameMain.setTransparency(1)
        self.content = DirectLabel(scale = 0.1, pos = (0.0, 0.0, base.a2dTop - 1),
                            frameColor = (0, 0, 0, 0), text="Congratulations, warrior! \n You successfully got OUT of that ugly place...", text_fg=(1,1,1,1))
        self.content.setTransparency(1)
        self.content.reparentTo(self.frameMain)
        self.btnExit = self.createButton("Leave", -0.75, ["Menu-Quit"])
        # background image from http://ajuntament.barcelona.cat/castelldemontjuic/en/activitats/noticies/we-open-dungeons-castle
        self.frameBackground = DirectFrame(image = ('models/winBackground.jpg'), sortOrder = (-1),
                frameSize = (base.a2dLeft, base.a2dRight, base.a2dBottom, base.a2dTop))
        self.frameBackground.reparentTo(render2d)
        self.hide()
    
    def createButton(self, text,verticalPos, eventArgs):
        btn = DirectButton(text=text,scale=0.15, pos=(0,0,verticalPos), command=base.messenger.send,
                            extraArgs=eventArgs, rolloverSound=None, clickSound=None)
        btn.reparentTo(self.frameMain)

    def show(self):
        self.frameMain.show()
        self.frameBackground.show()

    def hide(self):
        self.frameMain.hide()
        self.frameBackground.hide()