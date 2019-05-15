# home - runs the whole game
import os, sys, inspect, thread, time
from direct.showbase.ShowBase import ShowBase

from FSM import RunGame


# basic layout from panda3d manual, main function for the whole game
class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # start the game with menu
        self.state = RunGame()
        self.state.request('StartMenu')
        taskMgr.add(self.updateGameState, 'update')
    
    # updates the state of the game
    def updateGameState(self, task):
        if self.state.game.player.health <= 0 or self.state.game.player.atLevel >= 3:
            self.state.game.inGame = False
        if not self.state.game.inGame and self.state.game.player.health <= 0:
            self.state.request('EndMenu')
            return task.done
        if not self.state.game.inGame and self.state.game.player.atLevel >= 3:
            self.state.request('WinMenu')
            return task.done
        return task.cont
        
game = Game()
game.run()