# enemy - set up enemy statistics, movements, and actions
import sys, math, random
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from panda3d.core import CollisionNode
from panda3d.core import CollisionSphere
from panda3d.core import CollisionTraverser
from panda3d.core import CollideMask

# enemy object
class Enemy(DirectObject):
    def __init__(self, state, numb, player):
        # Model taken from https://www.blendswap.com/blends/view/76294
        self.enemyModel = base.loader.loadModel('models/knight')
        self.state = state
        self.player = player
        self.enemyModel.setScale(3.5, 3.5, 3.5)
        x = random.randint(-120, 120)
        y = random.randint(-100, 100)
        self.enemyModel.setPos(x, y, 3)
        self.enemyModel.setHpr(0, 0, 0)
        self.isAlive = True
        self.numb = numb
        self.speed = 0.1
        self.enemyModel.reparentTo(render)
        
        # fire
        self.fireballFired = Fireball(self)
        taskMgr.doMethodLater(5, self.fire, 'fireFireballs')
        
        # set up collision
        self.enemyCollide = CollisionSphere(0, 0, 0, 0.5)
        self.enemyCollisionNode = CollisionNode('enemy' + str(self.numb))
        self.enemyCollisionNode.addSolid(self.enemyCollide)
        self.enemyCollisionNode.setFromCollideMask(CollideMask.bit(0))
        self.enemyCollisionNode.setIntoCollideMask(CollideMask.allOff())
        self.collider = self.enemyModel.attachNewNode(self.enemyCollisionNode)
        
        # image taken from https://br.depositphotos.com/186812564/stock-photo-gray-steel-background-old-iron.html
        enemyTexture = loader.loadTexture("models/enemyTexture.jpg")
        self.enemyModel.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.enemyModel.setTexture(enemyTexture)
    
    # fire fireballs at the player
    def fire(self, task):
        if self.isAlive:
            self.fireballFired.isLive = False
            self.fireballFired.fireball.removeNode()
            newFireball = Fireball(self)
            self.fireballFired = newFireball
            task.delayTime += 1
            return task.again
        else:
            return task.done
    
    # move the enemy towards the target
    def move(self, target):
        target = target
        speed = self.speed
        # move to target if is alive
        if self.isAlive and self.state == 0:
            angle = self.enemyModel.getH()
            radian = math.radians(angle)
            
            targetPosX = target.getX()
            targetPosY = target.getY()
            enemyPosX = self.enemyModel.getX()
            enemyPosY = self.enemyModel.getY()
            margin = 1
            
            deltaX = abs(speed * math.sin(radian))
            deltaY = abs(speed * math.cos(radian))
            
            # stop enemy from moving if too close to player
            if abs(targetPosX - enemyPosX) <= margin or abs(targetPosY - enemyPosY) <= margin:
                deltaX = 0
                deltaY = 0
            
            if targetPosY < enemyPosY:
                deltaY = - deltaY
            if targetPosX < enemyPosX:
                deltaX = -deltaX
            
            self.enemyModel.setX(self.enemyModel.getX() + deltaX)
            self.enemyModel.setY(self.enemyModel.getY() + deltaY)


    # remove said enemy from nodepath when called
    def killEnemy(self, task):
        if self.player.damage and self.isAlive:
            self.player.changeStats(0, 1)
            self.isAlive = False
            self.fireballFired.isLive = False
            self.enemyModel.removeNode()
    
    # calculate where the enemy should face given the location of the player
    def lookAtPlayer(self, flyBot):
        flyBot = flyBot
        if self.isAlive:
            deltaX = self.enemyModel.getX() - flyBot.flyBot.getX()
            deltaY = self.enemyModel.getY() - flyBot.flyBot.getY()

            if deltaY == 0 and deltaX >= 0:
                change = 90
            elif deltaY == 0 and deltaX < 0:
                change = -90

            change = math.degrees(math.atan(deltaX/deltaY))
            
            
            if deltaY < 0:
                change = change + 180
            self.enemyModel.setH(-change)


# class object fireball
class Fireball(DirectObject):
    def __init__(self, enemy):
        # which enemy it is fired from
        self.enemy = enemy
        self.fireball = base.loader.loadModel('models/fireball')
        self.fireball.setScale(1, 1, 1)
        self.fireball.reparentTo(self.enemy.enemyModel)
        self.isLive = True
        
        # starting position from the enemy
        self.fireball.setPos(0, 0, 0)
        self.fireball.setHpr(0, 0, 0)
        
        # set up texture
        # image taken from https://www.youtube.com/user/AdamAndEveNOTsteve2/playlists?app=desktop
        fireballTexture = loader.loadTexture("models/fireballTexture.jpg")
        self.fireball.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.fireball.setTexture(fireballTexture)
        
        # move the fireball
        taskMgr.doMethodLater(0.05, self.move, 'moveFireball')
    
    # move the fireball
    def move(self, task):
        if self.isLive:
            self.speed = 1.5
            
            # get original position
            posY = self.fireball.getY()
            
            # move the ball
            self.fireball.setY(self.fireball, posY - self.speed)
            task.delayTime += 0.01
            
            return task.again
        else:
            return task.done
    
    # remove the fireball
    def removeFireball(self, task):
        self.isLive = False
        self.fireball.removeNode()