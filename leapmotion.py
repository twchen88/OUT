# Leap Motion - set up leap motion and export leap motion data to the game
import os, sys, inspect, thread, time
sys.path.insert(0, "LeapSDK/lib")

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# modified from leap motion mini lecture demo code
class LeapMotion(object):
    def __init__(self):
        self.controller = Leap.Controller()
        self.frame = self.controller.frame()
        self.data = []
        # outside of these bounds will not be considered movement
        self.yLowerBound = 25
        self.yUpperBound = 300
        self.xLowerBound = -140
        self.xUpperBound = 140
        self.zLowerBound = 40
        self.zUpperBound = -140
        # bounds on the screen
        self.xSceneUpperBound = 0.75
        self.xSceneLowerBound = -0.40
        self.ySceneUpperBound = 0.50
        self.ySceneLowerBound = 0.02
        self.zSceneLowerBound = 2.0
        self.zSceneUpperBound = 7.0
        self.xIncrement = (self.xSceneUpperBound - self.xSceneLowerBound) / (self.xUpperBound - self.xLowerBound)
        self.yIncrement = (self.ySceneUpperBound - self.ySceneLowerBound) / (self.yUpperBound - self.yLowerBound)
        self.zIncrement = (self.zSceneUpperBound - self.zSceneLowerBound) / abs(self.zUpperBound - self.zLowerBound)
        self.curFrame = None

    def updateLeapMotionData(self):
        self.frame = self.controller.frame()
    
    # get the data of where the palm is
    def getData(self):
        self.curFrame = self.frame
        hand = self.curFrame.hands[0]
        point = self.cleanData(hand.palm_position)
        self.data.append(point)
    
    # calculate where the sword should be on the screen given where the hand is
    def cleanData(self, pos):
        posX = pos[0]
        posY = pos[1]
        posZ = pos[2]
        if self.xLowerBound <= posX and posX <= self.xUpperBound and self.yLowerBound <= posY and posY <= self.yUpperBound and self.zUpperBound <= posZ and posZ <= self.zLowerBound:
            posX = int(posX - self.xLowerBound)
            posX *= self.xIncrement
            posX += self.xSceneLowerBound
            posY = int(posY - self.yLowerBound)
            posY *= self.yIncrement
            posY += self.ySceneLowerBound
            posZ = int(self.zLowerBound - posZ)
            posZ *= self.zIncrement
            posZ += self.zSceneLowerBound
            return (posX, posY, posZ)
        return None
    
    # returns the data point
    def exportData(self):
        if self.data == []:
            return None
        point = self.data.pop(0)
        if point == None:
            return None
        dataX = point[0]
        dataY = point[1]
        dataZ = point[2]
        return (dataX, dataY, dataZ)

