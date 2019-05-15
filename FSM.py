# FSM - set up states for the game to enter
from direct.fsm.FSM import FSM
import sys

import environment
import menu

# FSM object, basic setup from panda3d manual
class RunGame(FSM):
    def __init__(self):
        FSM.__init__(self, 'RunGame')
        # only make certain transitions legal
        FSM.defaultTransitions = {'Game': ['EndMenu', 'WinMenu'], 'StartMenu' : ['Game', 'Instructions'], 'Instructions': ['Game'], 'EndMenu': [], 'WinMenu' : []}
        self.startMenu = menu.StartMenu()
        self.instructionMenu = menu.Instructions()
        self.game = environment.Load()
        self.endMenu = menu.EndMenu()
        self.winMenu = menu.Win()

    def enterStartMenu(self):
        self.accept("Menu-Start", self.request, ["Game"])
        self.accept('Menu-Instructions', self.request, ['Instructions'])
        self.accept('escape', self.quit)
        self.accept("Menu-Quit", self.quit)
        self.game.starterMusic.play()
        self.startMenu.show()
    def exitStartMenu(self):
        self.ignore("Menu-Start")
        self.ignore("Menu-Quit")
        self.startMenu.hide()
    def enterInstructions(self):
        self.accept('Instructions-startGame', self.request, ['Game'])
        self.accept('Menu-Quit', self.quit)
        self.accept('escape', self.quit)
        self.instructionMenu.show()
    def exitInstructions(self):
        self.ignore('Instructions-startGame')
        self.ignore('Menu-Quit')
        self.instructionMenu.hide()
    def enterGame(self):
        self.game.startGame()
        self.game.starterMusic.stop()
        self.game.gameMusic.play()
        render.show()
    def exitGame(self):
        render.hide()
        self.game.gameMusic.stop()
    def enterEndMenu(self):
        self.endMenu.show()
        self.game.stopGame()
        self.accept('escape', self.quit)
        self.accept("Menu-Quit", self.quit)
        self.game.endMusic.play()
    def exitEndMenu(self):
        self.ignore("Menu-Quit")
        self.endMenu.hide()
        self.game.endMusic.stop()
    def enterWinMenu(self):
        self.winMenu.show()
        self.game.stopGame()
        self.accept('escape', self.quit)
        self.accept('Menu-Quit', self.quit)
        self.game.endMusic.play()
    def exitWinMenu(self):
        self.winMenu.hide()
        self.game.endMusic.stop()
        self.ignore("Menu-Quit")
    def quit(self):
        sys.exit()