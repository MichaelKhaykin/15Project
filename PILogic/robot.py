from __future__ import annotations
import math
from typing import List, Tuple
import cv2 as cv
import numpy as np
from numpy import ndarray

from enums import trackerStates

class robot:
    grid: List[List[int]]
    gridSize: int
    debugMode: bool
    cap: cv.VideoCapture
    debugMode: bool
    emptyCellIndex: tuple[int, int]
    emptyCellPos: tuple[int, int]
    
    mask_lowerBound: ndarray
    mask_upperBound: ndarray

    state: trackerStates

    def __init__(self: robot, gridSize: int, deviceID: int, debugMode: bool):
        self.gridSize = gridSize
        self.resetGrid()
        self.cap = cv.VideoCapture(deviceID)
        self.debugMode = debugMode
        self.test = 0

        self.mask_lowerBound = np.array([114, 124, 48])
        self.mask_upperBound = np.array([169, 255, 150])

        self.emptyCellPos = None

        self.emptyCellIndex = [gridSize - 1, gridSize - 1]

        self.state = trackerStates.Waiting

        if self.debugMode:
            cv.namedWindow('inrange')
            self.makeTrackBars()

    def update(self: robot):

        if cv.waitKey(1) & 0xFF == ord('q'):
            return
        
        if self.state == trackerStates.Waiting:
            self.cap.read()
        elif self.state == trackerStates.Following:
            self.track()
        elif self.state == trackerStates.Solving:
            pass
        
    def track(self: robot):

        _, upsidedownframe = self.cap.read()
        frame: ndarray = cv.rotate(upsidedownframe, cv.ROTATE_180)

        hsv: ndarray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        lower_bound = self.mask_lowerBound
        upper_bound = self.mask_upperBound
         
        if self.debugMode:
            lower_bound = np.array([self.minH(), self.minS(), self.minV()])
            upper_bound = np.array([self.maxH(), self.maxS(), self.maxV()])
        
        inrange = cv.inRange(hsv, lower_bound, upper_bound)

        if self.debugMode:
            cv.imshow('inrange', inrange)

        contours, hierarchy = cv.findContours(inrange, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        absminarea = 100
        contours = list(filter(lambda x: cv.contourArea(x) > absminarea, contours))

        if(len(contours) == 0):
            return

        if self.debugMode:
            contourImg = frame.copy()
            cv.drawContours(contourImg, contours, -1, (0,255,0), 3)
            cv.imshow('contour', contourImg)
            
        cnt = contours[0]
        min_area = cv.contourArea(cnt)

        for cont in contours:
            contArea = cv.contourArea(cont)
            if contArea < min_area and len(cont) == 4:
                cnt = cont
                min_area = cv.contourArea(cont)

        epsilon = 0.01*cv.arcLength(cnt,True)
        approx = cv.approxPolyDP(cnt,epsilon,True)

        if len(approx) == 0:
            return
    
        smallestx = approx[0][0][0]
        largestx = approx[0][0][0]
        for x in range(0, len(approx)):
            smallestx = min(smallestx, approx[x][0][0])
            largestx = max(largestx, approx[x][0][0])
        
        cellSize = largestx - smallestx

        moments = cv.moments(cnt)
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        
        minCellSize = 50
        if cellSize <= minCellSize: 
            return

        if self.debugMode:
            approxImg = frame.copy()
            cv.drawMarker(approxImg, (cx, cy), (0, 255, 0), cv.MARKER_STAR)
            cv.drawContours(approxImg, [approx], -1, (0, 0, 255), 3)
            cv.imshow('approx', approxImg)
            
        if self.emptyCellPos == None:
            self.emptyCellPos = [cx, cy]
            return
        
        #Get distance between them
        xDiff = cx - self.emptyCellPos[0]
        yDiff = cy - self.emptyCellPos[1]
        distance = math.sqrt(xDiff * xDiff + yDiff * yDiff)

        if distance >= cellSize // 2:
            
            newEmptyCell = None

            if abs(xDiff) > abs(yDiff):
                if xDiff > 0:
                    newEmptyCell = [self.emptyCellIndex[0] + 1, self.emptyCellIndex[1]]
                else:
                    newEmptyCell = [self.emptyCellIndex[0] - 1, self.emptyCellIndex[1]]
            else:
                if yDiff < 0:
                    newEmptyCell = [self.emptyCellIndex[0], self.emptyCellIndex[1] - 1]
                else:
                    newEmptyCell = [self.emptyCellIndex[0], self.emptyCellIndex[1] + 1]
    
            self.grid[self.emptyCellIndex[1]][self.emptyCellIndex[0]] = self.grid[newEmptyCell[1]][newEmptyCell[0]]
            self.grid[newEmptyCell[1]][newEmptyCell[0]] = 0
            self.emptyCellIndex = newEmptyCell
            self.test += 1
            
            if self.debugMode:
                self.printGrid()

        self.emptyCellPos = [cx, cy]

    def resetGrid(self: robot):
        self.grid = [[(i + j * self.gridSize + 1) % (self.gridSize * self.gridSize) 
                        for i in range(0, self.gridSize)] for j in range(0, self.gridSize)]

    def nothing(self: robot, x):
        pass

    def makeTrackBars(self: robot):
        #Minimum value of a trackbar is always zero, first number represents start pos
        cv.createTrackbar('Min H','inrange',114,180, self.nothing)
        cv.createTrackbar('Min S','inrange',124,255, self.nothing)
        cv.createTrackbar('Min V','inrange',48,255, self.nothing)
        
        cv.createTrackbar('Max H','inrange',169,180, self.nothing)
        cv.createTrackbar('Max S','inrange',255,255, self.nothing)
        cv.createTrackbar('Max V','inrange',150,255, self.nothing)

    def minH(self: robot):
        return cv.getTrackbarPos('Min H', 'inrange')

    def minS(self: robot):
        return cv.getTrackbarPos('Min S', 'inrange')

    def minV(self: robot):
        return cv.getTrackbarPos('Min V', 'inrange')

    def maxH(self: robot):
        return cv.getTrackbarPos('Max H', 'inrange')

    def maxS(self: robot):
        return cv.getTrackbarPos('Max S', 'inrange')

    def maxV(self: robot):
        return cv.getTrackbarPos('Max V', 'inrange')

    def printGrid(self: robot):
        print('----------------------')
        print(f'{self.test}')
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                print(self.grid[y][x], end=' ')
            print('')
        print('----------------------')