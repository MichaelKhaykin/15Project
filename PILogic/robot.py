from __future__ import annotations
import math
import socket
from typing import List, Tuple
import cv2 as cv
import numpy as np
from numpy import ndarray
from vertex import vertex
from graph import graph

from enums import trackerStates

class robot:
    emptyPositions: List[tuple[int, int]]
    gridSize: int
    debugMode: bool
    cap: cv.VideoCapture
    debugMode: bool
    emptyCellIndex: tuple[int, int]
    emptyCellPos: tuple[int, int]
    
    purple_mask_lowerBound: ndarray
    purple_mask_upperBound: ndarray

    yellow_mask_lowerBound: ndarray
    yellow_mask_upperBound: ndarray

    state: trackerStates

    gridLocations: list[tuple[int, int]]

    ignore: int = 0

    def __init__(self: robot, gridSize: int, deviceID: int, debugMode: bool):
        self.gridSize = gridSize
        self.cap = cv.VideoCapture(deviceID)
        self.debugMode = debugMode
        self.test = 0

        self.gridLocations = None
        self.purple_mask_lowerBound = np.array([125, 148, 173])
        self.purple_mask_upperBound = np.array([160, 255, 255])

        self.yellow_mask_lowerBound = np.array([0, 5, 190])
        self.yellow_mask_upperBound = np.array([47, 35, 255])

        self.emptyCellPos = None
        self.emptyCellIndex = [gridSize - 1, gridSize - 1]
        self.emptyPositions = [self.emptyCellIndex]

        self.path = []

        self.state = trackerStates.Waiting

        if self.debugMode:
            cv.namedWindow('inrange')
            self.makeTrackBars()

    def update(self: robot, sock):

        if cv.waitKey(1) & 0xFF == ord('q'):
            return
        
        if self.state == trackerStates.Waiting:
            self.cap.read()
        elif self.state == trackerStates.Calibrating:
            self.calibrate()
        elif self.state == trackerStates.Following:
            self.track()
        elif self.state == trackerStates.CalculateSolution:
            grid = self.makeGrid()
            self.path = self.getSolutionPath(grid)
            self.state = trackerStates.Solving
            bytesList = []
            for x in self.path:
                bytesList.append(x[0] * self.gridSize + x[1])
            
            failed = True
            while failed:
                try:
                    sock.sendto(bytearray(bytesList), ('192.168.1.226', 5000))
                    failed = False
                except socket.error:
                    pass
            
        elif self.state == trackerStates.Solving:
            pass

    def makeGrid(self):
        grid = [[(i + j * self.gridSize + 1) % (self.gridSize * self.gridSize) 
                        for i in range(0, self.gridSize)] for j in range(0, self.gridSize)]
        
        for i in range(0, len(self.emptyPositions) - 1):
            curEmptyCellPos = self.emptyPositions[i]
            nextEmptyCellPos = self.emptyPositions[i + 1]

            temp = grid[curEmptyCellPos[1]][curEmptyCellPos[0]]
            grid[curEmptyCellPos[1]][curEmptyCellPos[0]] = grid[nextEmptyCellPos[1]][nextEmptyCellPos[0]]
            grid[nextEmptyCellPos[1]][nextEmptyCellPos[0]] = temp
        return grid

    def calibrate(self: robot):

        if self.gridLocations != None:
            self.state = trackerStates.Waiting
            return

        _, upsidedownframe = self.cap.read()
        frame: ndarray = cv.rotate(upsidedownframe, cv.ROTATE_180)

        hsv: ndarray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        lower_bound = self.purple_mask_lowerBound
        upper_bound = self.purple_mask_upperBound
         
       # if self.debugMode:
        #    lower_bound = np.array([self.minH(), self.minS(), self.minV()])
         #   upper_bound = np.array([self.maxH(), self.maxS(), self.maxV()])
        
        inrange = cv.inRange(hsv, lower_bound, upper_bound)
        if self.debugMode:
            cv.imshow('inrange', inrange)

        contours, _ = cv.findContours(inrange, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        absminarea = 50
        contours = list(filter(lambda x: cv.contourArea(x) > absminarea, contours))

        if(len(contours) == 0):
            return

        if self.debugMode:
            contourImg = frame.copy()
            cv.drawContours(contourImg, contours, -1, (0,255,0), 3)
            cv.imshow('contour', contourImg)
        
        if self.ignore < 2:
            self.ignore += 1
            return

        centerOrderedByX = self.sort_contours(contours)
        if len(centerOrderedByX) == self.gridSize * self.gridSize:
            self.gridLocations = [(0, 0)] * 9
            for i in range(0, len(centerOrderedByX), self.gridSize):
                #sort this segment by y
                segment = sorted(centerOrderedByX[i:i+self.gridSize], key = lambda x:x[1])

                for j in range(0, self.gridSize):    
                    self.gridLocations[j * self.gridSize + int(i // 3)] = segment[j]
            
            self.state = trackerStates.Waiting
            print(self.gridLocations)
            self.ignore = 0
            return
        

    def sort_contours(self, contours):
        
        boundingBoxes = [cv.boundingRect(c) for c in contours]
        centers = [(c[0] + c[2] / 2, c[1] + c[3] / 2) for c in boundingBoxes]

        # sorting on x-axis 
        sortedByX = sorted(centers, key = lambda x:x[0])
        
        # return the list of sorted bounding boxes
        return sortedByX

    def track(self: robot):

        _, upsidedownframe = self.cap.read()
        frame: ndarray = cv.rotate(upsidedownframe, cv.ROTATE_180)

        hsv: ndarray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        lower_bound = self.yellow_mask_lowerBound
        upper_bound = self.yellow_mask_upperBound
         
        if self.debugMode:
            lower_bound = np.array([self.minH(), self.minS(), self.minV()])
            upper_bound = np.array([self.maxH(), self.maxS(), self.maxV()])
        
        inrange = cv.inRange(hsv, lower_bound, upper_bound)

        if self.debugMode:
            cv.imshow('inrange', inrange)


        yvals, xvals = (inrange > 0).nonzero()
        if len(xvals) == 0 or len(yvals) == 0:
            return
        cx = sum(xvals) / len(xvals)
        cy = sum(yvals) / len(yvals)
        pos = [cx, cy]

        minDist = self.DistSq(self.gridLocations[0], pos)
        cell = [0, 0]
        for i in range(0, len(self.gridLocations)):
            curPos = self.gridLocations[i]
            distSq = self.DistSq(curPos, pos)
            if minDist > distSq:
                minDist = distSq
                cell = [i % self.gridSize, int(i // self.gridSize)]

        if not self.emptyPositions[-1] == cell:
            self.emptyPositions.append(cell)
            print(cell)

        return

        contours, _ = cv.findContours(inrange, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        absminarea = 20
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
            if contArea < min_area:
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
        pos = (int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"]))
        
        minCellSize = 20
        if cellSize <= minCellSize: 
            #return
            pass
        if self.debugMode:
            approxImg = frame.copy()
            cv.drawMarker(approxImg, (pos[0], pos[1]), (0, 255, 0), cv.MARKER_STAR)
            cv.drawContours(approxImg, [approx], -1, (0, 0, 255), 3)
            cv.imshow('approx', approxImg)

       

    
    def DistSq(self, s, e):
        return (s[0] - e[0]) * (s[0] - e[0]) + (s[1] - e[1]) * (s[1] - e[1])

    def nothing(self: robot, x):
        pass

    def makeTrackBars(self: robot):
        l = self.yellow_mask_lowerBound
        u = self.yellow_mask_upperBound

        #Minimum value of a trackbar is always zero, first number represents start pos
        cv.createTrackbar('Min H','inrange',l[0],180, self.nothing)
        cv.createTrackbar('Min S','inrange',l[1],255, self.nothing)
        cv.createTrackbar('Min V','inrange',l[2],255, self.nothing)
        
        cv.createTrackbar('Max H','inrange',u[0],180, self.nothing)
        cv.createTrackbar('Max S','inrange',u[1],255, self.nothing)
        cv.createTrackbar('Max V','inrange',u[2],255, self.nothing)

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
        pass
        #print('----------------------')
        #print(f'{self.test}')
        #for y in range(self.gridSize):
         #   for x in range(len(self.grid[y])):
          #      print(self.grid[y][x], end=' ')
           # print('')
        #print('----------------------')

    

    def getSolutionPath(self, grid) -> list[tuple[int, int]]:
        gridSize: int = len(grid)
        g: graph = graph(gridSize, gridSize)

        #Get this from camera at some point
        startVertex: vertex = vertex()
        startVertex.Value = grid
        
        goalArr: list[list[int]] = [[(i + j * gridSize + 1) % (gridSize * gridSize) 
                                    for i in range(0, gridSize)] for j in range(0, gridSize)]
        goalVertex: vertex = vertex()
        goalVertex.Value = goalArr
        
        grids = g.AStar(startVertex, goalVertex)
        grids.reverse()
        
        #Record locations of empty cells, since those are the places we need to click
        clickLocations = []
        for x in range(1, len(grids)):
            zeroLocation = next((i, j) for i in range(0, self.gridSize) for j in range(0, self.gridSize) if grids[x].Value[i][j] == 0)
            clickLocations.append(zeroLocation)
                
        return clickLocations