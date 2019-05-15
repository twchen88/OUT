# environment - set up background and interactions between player, enemy, and the environment
import os, sys, inspect, thread, time
import random, math
sys.path.insert(0, "LeapSDK/lib")

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from direct.task.Task import Task
from panda3d.core import CollisionHandlerEvent, CollisionHandlerPusher
from panda3d.core import CollisionNode, CollideMask, CollisionTraverser
from panda3d.core import CollisionRay, CollisionBox

import player
import enemy
import leapmotion

# basic layout from panda3d manual, main function for the whole game
class Load():
    def __init__(self):
        # import leap motion
        self.leap = leapmotion.LeapMotion()
        # disable mouse control
        base.disableMouse()
        render.hide()
        self.inGame = True
        
        # menu music
        # taken from https://www.youtube.com/watch?v=2iEWbHJDlo4&list=PLzCxunOM5WFIudfMTgJzXkOE-xbVWrpIF&index=7
        self.starterMusic = loader.loadMusic('musics/starterMenuBackground.ogg')
        self.starterMusic.setLoop(True)
        # taken form https://www.youtube.com/watch?v=I0vEzblcnPA&list=PLzCxunOM5WFIudfMTgJzXkOE-xbVWrpIF&index=18
        self.endMusic = loader.loadMusic('musics/endMusic.ogg')
        self.endMusic.setLoop(True)
        
        # game music from https://www.youtube.com/watch?v=mNFNOEi9QV4&list=PLzCxunOM5WFK7WGa3wGjlONp_9R66a2zz&index=8
        self.gameMusic = loader.loadMusic('musics/gameMusic.ogg')
        self.gameMusic.setLoop(True)
        
        # import flybot, enemy, door, chests, key, and player
        self.flyBot = FlyBot()
        self.player = player.Player(self.flyBot)
        self.enemies = []
        self.numbEnemies = 0
        keyChest = random.randint(0, 3)
        # self.key = Key(keyChest)
        self.door = Door(225, 190, self.flyBot)
        self.walls = []
        self.chests = []
    
    def startGame(self):
        # Load the map.
        self.environ = loader.loadModel("models/background_model")
        # Reparent the model to render.
        self.environ.reparentTo(render)
        # Apply scale and position transforms on the model.
        # image taken from http://motorbikes-passion.info/scary-dark-room.html
        myTexture = loader.loadTexture("models/backgroundtexture.jpg")
        self.environ.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldCubeMap)
        self.environ.setTexture(myTexture)
        self.environ.setScale(1, 1, 1)
        self.environ.setPos(0, 0, 0)
        self.environ.reparentTo(render)
        
        
        # random generate map
        self.numbWalls = 4
        walls = generateRoom([], self.numbWalls)
        # if random generation fails, input default map
        if walls == None:
            walls = [(120, 30, 0), (-100, 80, 90), (-130, -70, 0), (50, -50, 90)]
        # load wall models in respective location
        for wall in walls:
            x, y, angle = wall
            newWall = Wall(x, y, angle)
            self.walls.append(newWall)
        
        # generate chests in random areas
        chests = generateChestLocation(walls)
        for chest in chests:
            x, y, chestNumb = chest
            newChest = Chest(self.player, self.flyBot, x, y, chestNumb)
            self.chests.append(newChest)
        
        
        # display player stats
        self.display = self.player.displayStats()
        
        
        # run collision settings
        base.cTrav = CollisionTraverser()
        # Set up collision for environment
        self.backgroundCollide = CollisionRay()
        self.backgroundNode = CollisionNode('backgroundCollider')
        self.backgroundNode.addSolid(self.backgroundCollide)
        self.backgroundNode.setFromCollideMask(CollideMask.bit(0))
        self.backgroundNode.setIntoCollideMask(CollideMask.allOff())
        self.backgroundCollider = self.environ.attachNewNode(self.backgroundNode)

        # call all functions that deal with collisions
        taskMgr.add(self.swordHitEnemy, 'killEnemy')
        self.wallCollisions()
        taskMgr.add(self.fireballHitPlayer, 'fireballHits')
        
        # load sound effects
        # sound taken from https://bigsoundbank.com/detail-0129-sword.html
        self.swordCut = loader.loadSfx('musics/0129.ogg')
        # sound taken from https://bigsoundbank.com/detail-0437-shot-beretta-m12-9-mm.html
        self.fireballHit = loader.loadSfx('musics/0437.ogg')

        # run quitGame
        self.quitGame()
        
        # Set up initial camera position
        base.camera.setPos(0, 0, 0)
        base.camera.setHpr(0, 0, 0)
        base.camera.reparentTo(self.flyBot.flyBot)
        # import player controls from player file
        self.playerControl = player.KeyboardControl(self.flyBot, self.chests, self.door, self.walls, self.player)
        
        # import leap motion control
        self.leapControl = player.swordControl(self.leap, self.player)
        taskMgr.add(self.leapControl.swingsword, 'swingsword')
        
        # spawn new enemies
        sec = 5 - self.player.atLevel
        taskMgr.doMethodLater(sec, self.spawnEnemies, 'createNewEnemy')
    
        # test enemy movements
        taskMgr.add(self.enemyMovements, 'enemyMovements')
        
        # Game AI
        AI = GameAI(self.enemies, self.flyBot)
        taskMgr.add(AI.makeDecision, 'enemyStateDetermination')
    
    # stop all tasks
    def stopGame(self):
        taskMgr.remove('checkGameState')
        taskMgr.remove('enemyStateDetermination')
        taskMgr.remove('enemyMovements')
        taskMgr.remove('createNewEnemy')
        taskMgr.remove('swingsword')
        taskMgr.remove('fireballHits')
        taskMgr.remove('killEnemy')
        taskMgr.remove("playerMove")
        taskMgr.remove('openChestOrDoor')
        taskMgr.remove('moveFireball')
        taskMgr.remove('fireFireballs')

    # allow keyboard exit
    def quitGame(self):
        textObject = OnscreenText(text = 'ESC to exit game', pos=(-0.25, -0.05), scale = 0.05, parent = base.a2dTopRight)
        # The key esc will exit the game
        base.accept('escape', sys.exit)
    
    # create new enemies
    def spawnEnemies(self, task):
        if len(self.enemies) < 20:
            # default state is stay
            self.numbEnemies += 1
            newEnemy = enemy.Enemy(1, self.numbEnemies, self.player)
            self.enemies.append(newEnemy)
        task.delayTime += 1
        return task.again
    
    # moves the enemies towards the player
    def enemyMovements(self, task):
        for enemy in self.enemies:
            enemy.lookAtPlayer(self.flyBot)
            if enemy.state == 0:
                enemy.move(self.flyBot.flyBot)
            if enemy.state == 2:
                randomChest = random.randint(0, 3)
                doorOrChest = random.randint([self.door.door, self.chests[randomChest].chestModel])
                enemy.move(doorOrChest)
        return task.cont
    
    # Collision functions, called in init
    def wallCollisions(self):
        # Pusher so that the player cannot move past the walls
        self.playerPusher = CollisionHandlerPusher()
        base.cTrav.addCollider(self.flyBot.playerCollider, self.playerPusher)
        self.playerPusher.addCollider(self.flyBot.playerCollider, self.flyBot.flyBot)
        
        self.enemyPusher = CollisionHandlerPusher()
        for enemy in self.enemies:
            base.cTrav.addCollider(enemy.collider, self.enemyPusher)
            self.enemyPusher.addCollider(enemy.collider, enemy.enemyModel)
    
    
    def swordHitEnemy(self, task):
        # When the sword collides with enemy, enemy dies
        for enemy in self.enemies:
            self.playerKill = CollisionHandlerEvent()
            base.cTrav.addCollider(enemy.collider, self.playerKill)
            self.playerKill.addInPattern('%fn-into-%in')
    
        # perform the task
            self.kill = DirectObject()
            self.kill.accept('enemy'+ str(enemy.numb) + '-into-swordCollider', enemy.killEnemy)
            self.swordHit = DirectObject()
            self.swordHit.accept('enemy'+ str(enemy.numb) + '-into-swordCollider', self.swordHitSound)
            if not enemy.isAlive:
                self.enemies.remove(enemy)
        return task.cont
    
    # play the sound when the sword hits an ememy
    def swordHitSound(self, *args):
        if self.player.damage:
            self.swordCut.play()
    
    # create collision system for fireballs based on the location of the player
    # and the location of a given enemy
    def fireballHitPlayer(self, task):
        for enemy in self.enemies:
            if enemy.fireballFired.isLive:
                # When fireball collides with player, player health reduces
                playerX = self.flyBot.flyBot.getX()
                playerY = self.flyBot.flyBot.getY()
                margin = 5
                
                enemyH = math.sin(math.radians(enemy.enemyModel.getH()))
                fireballX = enemy.enemyModel.getX()
                fireballY = enemy.enemyModel.getY() + enemyH * enemy.fireballFired.fireball.getY()
                enemyY = enemy.enemyModel.getY()
                playerH = self.flyBot.flyBot.getH()
                
                if abs(fireballY) > 230 or abs(fireballX) > 230:
                    enemy.fireballFired.removeFireball(task)
                
                if (playerH > -45 and playerH < 45) or (playerH > 135) or (playerH < -135):
                    if playerX - margin <= fireballX and playerX + margin >= fireballX:
                        if (abs(enemy.enemyModel.getH()) <= 45 and fireballY >= playerY) or\
                        (abs(enemy.enemyModel.getH()) >= 135 and fireballY <= playerY):
                            self.fireballHit.play()
                            self.player.changeStats(-5, 0)
                            enemy.fireballFired.removeFireball(task)
                
                else:
                    if playerY - margin <= fireballY and playerY + margin >= fireballY:
                        if (enemy.enemyModel.getH() <= 0 and fireballX >= playerX) or\
                            (enemy.enemyModel.getH() > 0 and fireballX <= playerX):
                            self.fireballHit.play()
                            self.player.changeStats(-5, 0)
                            enemy.fireballFired.removeFireball(task)
        
        return task.cont


# allow camera and player to move independently
class FlyBot(DirectObject):
    def __init__(self):
        self.flyBot = base.loader.loadModel('models/flyBot')
        self.flyBot.setScale(1, 1, 1)
        self.flyBot.setPos(0, 0, 4)
        self.flyBot.setHpr(0, 0, 0)
        self.flyBot.reparentTo(render)
        self.moved = False
                
        self.playerCollide = CollisionBox(0, 3, 1.5, 1.5)
        self.playerNode = CollisionNode('player')
        self.playerNode.addSolid(self.playerCollide)
        self.playerNode.setFromCollideMask(CollideMask.bit(0))
        self.playerNode.setIntoCollideMask(CollideMask.allOff())
        self.playerCollider = self.flyBot.attachNewNode(self.playerNode)

# basic game AI that allow enemies to collaborate with each other
class GameAI(DirectObject):
    def __init__(self, enemies, flyBot):
        self.enemies = enemies
        self.flyBot = flyBot
        self.state = ['moveToPlayer', 'stay', 'moveToObjects']
    
    # check the state of the game
    def checkGameState(self):
        self.movingToPlayer = 0
        self.stay = 0
        self.around = 0
        for enemy in self.enemies:
            # count how many enemeis are in each state
            if enemy.state == 0:
                self.movingToPlayer += 1
            elif enemy.state == 1:
                self.stay += 1
            # check if the enemy is around the player
            if self.aroundPlayer(self.flyBot, enemy):
                self.around += 1
    
    # determine state of the enemy
    def makeDecision(self, task):
        for enemy in self.enemies:
            # check game state everytime before making a decision
            self.checkGameState()
            # if enemy is around the player, move to the player
            if self.aroundPlayer(self.flyBot, enemy):
                enemy.state = 0
            # if less than three enemies are moving to player and less than two around player and is not moving, set the enemy state to moving to player
            elif self.movingToPlayer < 3 and self.around < 2 and enemy.state == 1:
                enemy.state = 0
            # if there are more than three enemies staying, move them towars an object
            elif self.stay > 3 and enemy.state == 1:
                enemy.state = 2
            # or else, stop the enemy from moving
            else:
                enemy.state = 1
            # speed enemy up if it is around the player
            if self.aroundPlayer(self.flyBot, enemy):
                enemy.speed = 0.25
        return task.cont

    # check if enemy is within 100 unit radius of the player
    def aroundPlayer(self, flyBot, enemy):
        player = flyBot.flyBot
        enemy = enemy
        if enemy.isAlive:
            pX = player.getX()
            pY = player.getY()
            eX = enemy.enemyModel.getX()
            eY = enemy.enemyModel.getY()
            
            deltaX = eX - pX
            deltaY = eY - pY
            
            return ((deltaX)**2 + (deltaY)**2)**0.5 <= 100



# create chest objects
class Chest(DirectObject):
    def __init__(self, player, flyBot, x, y, numb):
        # Taken from https://www.blendswap.com/blends/view/52166
        self.x = x
        self.y = y
        self.chestNumb = numb
        self.isUsed = False
        self.chestModel = base.loader.loadModel('models/chest')
        self.chestModel.setPos(self.x, self.y, 0.5)
        self.player = player
        self.flyBot = flyBot.flyBot
        self.chestModel.reparentTo(render)
        
        # image taken from https://www.topsimages.com/images/silver-sequins-aa.html
        chestTexture = loader.loadTexture('models/chestTexture.jpg')
        self.chestModel.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.chestModel.setTexture(chestTexture)
    
    # check if player is nearby
    def playerNearby(self):
        cx = self.chestModel.getX()
        cy = self.chestModel.getY()
        px = self.flyBot.getX()
        py = self.flyBot.getY()
                        
        return ((cx - px)**2 + (cy - py)**2)**0.5 < 20
    
    # remove the chest from the game and add 5 health to the player
    def openChest(self):
        # sound taken from https://freesound.org/people/sqeeeek/sounds/381854/
        chestOpen = loader.loadSfx('musics/chestOpen.wav')
        chestOpen.play()
        self.chestModel.hide()
        if not self.isUsed:
            self.player.changeStats(5, 0)
            self.isUsed = True
    
    # make the chests active again at given location after moving to a new room
    def renew(self, newPos):
        self.isUsed = False
        self.chestModel.show()
        nx, ny, chestNumb = newPos
        self.chestModel.setPos(nx, ny, 0.5)
        self.chestNumb = chestNumb
        
# create door object
class Door(DirectObject):
    def __init__(self, x, y, flyBot):
        # Taken from https://www.blendswap.com/blends/view/55370
        self.door = base.loader.loadModel('models/door')
        self.x = x
        self.y = y
        self.door.setPos(self.x, self.y, 0.5)
        self.door.setHpr(90, 0, 0)
        self.door.setScale(3, 3, 3)
        self.flyBot = flyBot.flyBot
        self.door.reparentTo(render)
        
        # image taken from http://wallpapercraft.site/42400-brushed-steel.html
        doorTexture = loader.loadTexture("models/doorTexture.jpeg")
        self.door.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.door.setTexture(doorTexture)
    
    # check if player is nearby
    def playerNearby(self):
        cx = self.x
        cy = self.y
        px = self.flyBot.getX()
        py = self.flyBot.getY()
                        
        return abs(cx - px) <=35 and abs(cy - py) <= 10
    
    # create a new room with chests when the door opens
    def openDoor(self):
        # sound taken from https://freesound.org/people/NeoSpica/sounds/425090/
        doorOpen = loader.loadSfx('musics/doorOpen.wav')
        doorOpen.play()
        newRoom = generateRoom([], 4)
        if newRoom == None:
            newRoom = [(120, 30, 0), (-100, 80, 90), (-130, -70, 0), (50, -50, 90)]
        newChests = generateChestLocation(newRoom)
        self.flyBot.setPos(0, 0, 4)
        return (newRoom, newChests)
        

# wall object
class Wall(DirectObject):
    def __init__(self, x, y, angle):
        self.wall = base.loader.loadModel('models/wall')
        self.wall.setPos(x, y, 0)
        self.wall.setScale(10, 10, 10)
        self.wall.setH(angle)
        self.wall.reparentTo(render)
        
        # image taken from https://www.pinterest.com/pin/685602743251144929/?lp=true
        wallTexture = loader.loadTexture('models/walltest.jpg')
        self.wall.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldCubeMap)
        self.wall.setTexProjector(TextureStage.getDefault(), render, self.wall)

        self.wall.setTexture(wallTexture)
        
        self.wallCollide = CollisionRay()
        self.wallNode = CollisionNode('wall')
        self.wallNode.addSolid(self.wallCollide)
        self.wallNode.setFromCollideMask(CollideMask.bit(0))
        

        self.wallNode.setIntoCollideMask(CollideMask.allOff())
        self.wallCollider = self.wall.attachNewNode(self.wallNode)
    
    # move the wall to create a new room
    def move(self, newPos):
        nx, ny, nAngle = newPos
        self.wall.setPos(nx, ny, 0)
        self.wall.setH(nAngle)

# recursively generate all wall locations using backtracking
def generateRoom(walls, numbWalls = 4):
    newWalls = []
    if len(walls) == numbWalls:
        return walls
    for i in range(20):
        newWalls += [generateWall()]
    for newWall in newWalls:
        if validWall(newWall, walls):
            walls.append(newWall)
            tmp = generateRoom(walls)
            if tmp != None:
                return tmp
            walls.remove(newWall)
    return None
    
# check to see if new wall is valid
def validWall(newWall, walls):        
    vertMinMargin = 50
    vertMaxMargin = 280
    horMinMargin = 220
    horMaxMargin = 250
    
    newX, newY, newAngle = newWall     
    horCount = 0
    vertCount = 0 
    
    for curWall in walls:
        curX, curY, curAngle = curWall
        if curWall == newWall:
            return False
        if (abs(curX - newX) > horMaxMargin or abs(curX - newX) < horMinMargin) and curAngle == newAngle:
            return False
        if (abs(curY - newY) > vertMaxMargin or abs(curY - newY) < vertMinMargin) and curAngle == newAngle:
            return False
    return True

# randomly generate a wall within a given dimension
def generateWall():
    vertMax = 120
    vertMin = -120
    horMax = 125
    horMin = -125
    x = random.randint(horMin, horMax)
    y = random.randint(vertMin, vertMax)
    angle = random.choice([0, 90])
    return (x, y, angle)

# randomly generate chests based on where the walls are
def generateChestLocation(walls):
    length = 110
    width = 25
    chestNumb = 0
    chests = []
    
    for wall in walls:
        x, y, angle = wall
        if angle == 0:
            upperX = x + length
            lowerX = x - length
            upperY = y + width
            lowerY = y - width
            
            cx = random.randint(lowerX, upperX)
            cy1 = random.randint(upperY, 190)
            cy2 = random.randint(-190, lowerY)
            cy = random.choice([cy1, cy2])
        else:
            upperX = x + width
            lowerX = x - width
            upperY = y + length
            lowerY = y - length
            
            cx1 = random.randint(upperX, 225)
            cx2 = random.randint(-225, lowerX)
            cx = random.choice([cx1, cx2])
            cy = random.randint(lowerY, upperY)
        
        chests.append((cx, cy, chestNumb))
        chestNumb += 1
    return chests

