# Player - set up player statistics, movement, and action
import sys
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from direct.task.Task import Task
from panda3d.core import *
from panda3d.core import CollisionNode
from panda3d.core import CollisionSphere, CollisionTube, CollisionRay
from panda3d.core import CollisionTraverser
from panda3d.core import BitMask32

# player object
class Player(DirectObject):
    def __init__(self, flyBot):
        # sword model from https://www.blendswap.com/blends/view/70259
        self.sword = base.loader.loadModel('models/swordModel_1')
        self.sword.setScale(0.1, 0.1, 0.1)
        self.sword.setPos(0.1, 2, 0.2)
        self.sword.setHpr(-30, 0, 30)
        self.flyBot = flyBot.flyBot
        self.sword.reparentTo(self.flyBot)
        self.damage = True
        self.enemiesKilled = 0
        self.health = 50
        self.atLevel = 0
        
        # image from https://cellcode.us/quotes/illustrator-gradients-color.html
        swordTexture = loader.loadTexture("models/playertexture.jpg")
        self.sword.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.sword.setTexture(swordTexture)
        
        # add built-in collision object
        self.swordCollider = self.sword.find("**/swordCollider")

    
    # display player's current stats
    def displayStats(self):
        self.displayText = DirectLabel(text = 'CURRENT LEVEL: %d \n CURRENT HEALTH: %d \n ENEMIES KILLED: %d' %(self.atLevel, self.health, self.enemiesKilled), scale = 0.06, frameColor=(1, 1, 1, 1), frameSize=(-5.25, 6.00, -2.50, 1.5))
        self.displayText.setPos(-1, 0, 0.9)
        
    # change displayed stats
    def changeStats(self, health, enemies):
        # remove the display screen
        self.displayText.removeNode()
        # create new display screen with new stats
        self.health += health
        self.enemiesKilled += enemies
        self.displayStats()
        if self.health <= 0:
            self.displayText.hide()
    

# control the sword using leap motion
class swordControl(DirectObject):
    def __init__(self, leap, player):
        self.leap = leap
        self.player = player
        self.sword = player.sword
    # given where the hand is , move the sword around
    def swingsword(self, task):
        self.leap.updateLeapMotionData()
        self.leap.getData()
        self.dataPoint = self.leap.exportData()
        # disable sword function if hand is not detected
        if self.dataPoint == None:
            self.sword.hide()
            self.player.damage = False
            return task.cont
        else:
            self.sword.show()
            self.player.damage = True
            self.x = self.dataPoint[0]
            self.z = self.dataPoint[1]
            self.y = self.dataPoint[2]
            
            self.sword.setX(self.x)
            self.sword.setZ(self.z)
            self.sword.setY(self.y)
            return task.cont




# First person camera control and various commands with keyboard.
class KeyboardControl(DirectObject):
    def __init__(self, flyBot, chests, door, walls, player):
        self.flyBot = flyBot.flyBot
        self.chests = chests
        self.door = door
        self.walls = walls
        self.player = player
        self.setKeyboard()
        taskMgr.add(self.move, "playerMove")
        taskMgr.add(self.open, 'openChestOrDoor')
        self.keyMap = {"left" : 0, "right" : 0, "forward" : 0, "backward" : 0, 
                        "lookLeft" : 0, "lookRight" : 0, 'openChest' : False,
                         'openDoor' : False}
    
    # set the key to respective value
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    # set key to value based on key pressed.
    def setKeyboard(self):
        # direction key
        self.accept('a', self.setKey, ['left', 1])
        self.accept('a-up', self.setKey, ['left', 0])
        self.accept('d', self.setKey, ['right', 1])
        self.accept('d-up', self.setKey, ['right', 0])
        self.accept('w', self.setKey, ['forward', 1])
        self.accept('w-up', self.setKey, ['forward', 0])
        self.accept('s', self.setKey, ['backward', 1])
        self.accept('s-up', self.setKey, ['backward', 0])
        
        # look left and right key
        self.accept('q', self.setKey, ['lookLeft', 1])
        self.accept('e', self.setKey, ['lookRight', 1])
        self.accept('q-up', self.setKey, ['lookLeft', 0])
        self.accept('e-up', self.setKey, ['lookRight', 0])
        
        # open chests or doors
        self.accept('o', self.setKey, ['openChest', True])
        self.accept('space', self.setKey, ['openDoor', True])
        self.accept('o-up', self.setKey, ['openChest', False])
        self.accept('space-up', self.setKey, ['openDoor', False])
    
    # Modified from mini lecture demo file.
    def move(self, task):
        if self.keyMap["forward"] > 0:
            self.flyBot.setY(self.flyBot, self.flyBot.getY(self.flyBot) + 0.5)
        
        elif self.keyMap["backward"] > 0:
            self.flyBot.setY(self.flyBot, self.flyBot.getY(self.flyBot) - 0.5)

        elif self.keyMap["left"] > 0:
            self.flyBot.setX(self.flyBot, self.flyBot.getX(self.flyBot) - 0.5)
        
        elif self.keyMap["right"] > 0:
            self.flyBot.setX(self.flyBot, self.flyBot.getX(self.flyBot) + 0.5)
        
        elif self.keyMap["lookLeft"] > 0:
            self.flyBot.setH(self.flyBot, self.flyBot.getH(self.flyBot) + 1)
        
        elif self.keyMap["lookRight"] > 0:
            self.flyBot.setH(self.flyBot, self.flyBot.getH(self.flyBot) - 1)
        
        if self.flyBot.getZ() != 4.0:
            self.flyBot.setZ(4)
    
        return task.cont
    
    # open chests or door
    def open(self, task):
        if self.keyMap['openChest']:
            for chest in self.chests:
                if chest.playerNearby():
                    chest.openChest()
        if self.keyMap['openDoor']:
            if self.door.playerNearby() and (self.player.atLevel + 1) * 15 <= self.player.enemiesKilled:
                self.player.atLevel += 1
                if self.player.atLevel != 3:
                    self.player.changeStats(15, 0)
                newWalls, newChests = self.door.openDoor()
                for i in range(len(self.walls)):
                    self.walls[i].move(newWalls[i])
                for i in range(len(self.chests)):
                    self.chests[i].renew(newChests[i])
        return task.cont
    