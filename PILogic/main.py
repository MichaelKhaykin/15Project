from sre_constants import CATEGORY_UNI_DIGIT
import cv2 as cv
import numpy as np
from numpy import ndarray
from graph import Graph
from vertex import Vertex
from typing import List, Dict
import math

def graphTesting(startGrid: List[List[int]]):
    graph: Graph = Graph(len(startGrid), len(startGrid))

    #Get this from camera at some point
    startVertex: Vertex = Vertex()
    startVertex.Value = startGrid
    
    goalArr: list[list[int]] = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    goalVertex: Vertex = Vertex()
    goalVertex.Value = goalArr
    
    path = graph.AStar(startVertex, goalVertex)
    print(len(path))

def SplitImage(img: ndarray, gridSize: int) -> List[ndarray]:
    cuts: list[ndarray] = []
    height: int = img.shape[0] // gridSize
    width: int = img.shape[1] // gridSize

    for y in range(0, gridSize):
        for x in range(0, gridSize):
            roi: ndarray = img[y * height : y * height + height, x * width : x * width + width]
            cuts.append(roi)
    
    return cuts

def GetGrid(ogImg: ndarray, unsortedImg: ndarray, gridSize: int) -> List[List[int]]:
    
    ogImgCuts: list[ndarray] = SplitImage(ogImg, gridSize)
    unsortedCuts: list[ndarray] = SplitImage(unsortedImg, gridSize)

    calculatedGrid: list[list[int]] =  [[0 for i in range(3)] for j in range(3)]
    
    channels = [0]
    mask = None
    histSize = [256]
    ranges = [0, 256]

    ogImgMap = {}
    for i in range(0, len(ogImgCuts)):
        ogImgMap[i] = cv.calcHist([ogImgCuts[i]], channels, mask, histSize, ranges)
        cv.normalize(ogImgMap[i], ogImgMap[i], alpha=0, beta=1, norm_type=cv.NORM_MINMAX)
    
    unsortedMap = {}
    for i in range(0, len(unsortedCuts)):
        unsortedMap[i] = cv.calcHist([unsortedCuts[i]], channels, mask, histSize, ranges)
        cv.normalize(unsortedMap[i], unsortedMap[i], alpha=0, beta=1, norm_type=cv.NORM_MINMAX)
    
    for i in range(0, len(ogImgCuts) - 1):

        max: float = 0
        x: int = 0
        y: int = 0

        for j in range(0, len(unsortedCuts)):

            count: float = abs(cv.compareHist(ogImgMap[i], unsortedMap[j], cv.HISTCMP_CORREL)) * 100
            if count >= max:
                max = count
                x = j % gridSize
                y = j // gridSize

        if max == 0:
            raise Exception('bad')
        calculatedGrid[y][x] = i + 1

    return calculatedGrid
    
def nothing(x):
    pass

def MakeBar():
    #Minimum value of a trackbar is always zero, first number represents start pos
    cv.createTrackbar('Min H','inrange',114,180, nothing)
    cv.createTrackbar('Min S','inrange',124,255, nothing)
    cv.createTrackbar('Min V','inrange',48,255, nothing)
    
    cv.createTrackbar('Max H','inrange',169,180, nothing)
    cv.createTrackbar('Max S','inrange',255,255, nothing)
    cv.createTrackbar('Max V','inrange',150,255, nothing)

def MinH():
    return cv.getTrackbarPos('Min H', 'inrange')

def MinS():
    return cv.getTrackbarPos('Min S', 'inrange')

def MinV():
    return cv.getTrackbarPos('Min V', 'inrange')

def MaxH():
    return cv.getTrackbarPos('Max H', 'inrange')

def MaxS():
    return cv.getTrackbarPos('Max S', 'inrange')

def MaxV():
    return cv.getTrackbarPos('Max V', 'inrange')

def printGrid(grid):
    print('----------------------')
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            print(grid[y][x], end=' ')
        print('')
    print('----------------------')

def MakeGrid(gridSize: int) -> List[List[int]]:
    grid: list[list[int]] = [[(i + j * gridSize + 1) % (gridSize * gridSize) for i in range(0, gridSize)] for j in range(0, gridSize)]
    return grid

def main():

    cv.namedWindow('inrange')
    MakeBar()

    cap = cv.VideoCapture(0)
    
    gridSize: int = 4
    #grid: List[List[int]] = GetGrid("images/minesweeper.png", "images/stanshuffle.png", gridSize)
    #print(grid)
    #graphTesting(grid)

    minesweeper: ndarray = cv.imread('images/minesweeper.png')

    #testgrid = GetGrid(minesweeper, cv.imread('testimg.png'), 3)

    prevTl = None

    currGrid: list[list[int]] = MakeGrid(gridSize)
    emptyCellIndex = [gridSize - 1, gridSize - 1]


    while(True):

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        _, upsidedownframe = cap.read()
        frame: ndarray = cv.rotate(upsidedownframe, cv.ROTATE_180)

        hsv: ndarray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        purple_lowerBound = np.array([MinH(), MinS(), MinV()])
        purple_upperBound = np.array([MaxH(), MaxS(), MaxV()])
        inrange = cv.inRange(hsv, purple_lowerBound, purple_upperBound)

        #cv.imshow('inrange', inrange)

        contours, hierarchy = cv.findContours(inrange, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        absminarea = 100
        contours = list(filter(lambda x: cv.contourArea(x) > absminarea, contours))

        if(len(contours) == 0):
            continue

        contourImg = frame.copy()
        #cv.drawContours(contourImg, contours, -1, (0,255,0), 3)

        #cv.imshow('contour', contourImg)
        
        
        cnt = contours[0]
        min_area = cv.contourArea(cnt)

        for cont in contours:
            contArea = cv.contourArea(cont)
            if contArea < min_area and len(cont) == 4:
                cnt = cont
                min_area = cv.contourArea(cont)

        perimeter = cv.arcLength(cnt,True)
        epsilon = 0.01*cv.arcLength(cnt,True)
        approx = cv.approxPolyDP(cnt,epsilon,True)

        if len(approx) == 0:
            continue

       
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
            continue

        approxImg = frame.copy()
        cv.drawMarker(approxImg, (cx, cy), (0, 255, 0), cv.MARKER_STAR)
        cv.drawContours(approxImg, [approx], -1, (0, 0, 255), 3)
        cv.imshow('approx', approxImg)
        
        if prevTl == None:
            prevTl = [cx, cy]
            continue
        
        #Get distance between them
        xDiff = cx - prevTl[0]
        yDiff = cy - prevTl[1]
        distance = math.sqrt(xDiff * xDiff + yDiff * yDiff)

        if distance >= cellSize // 2:
            
            newEmptyCell = None

            if abs(xDiff) > abs(yDiff):
                if xDiff > 0:
                    newEmptyCell = [emptyCellIndex[0] + 1, emptyCellIndex[1]]
                else:
                    newEmptyCell = [emptyCellIndex[0] - 1, emptyCellIndex[1]]
            else:
                if yDiff < 0:
                    newEmptyCell = [emptyCellIndex[0], emptyCellIndex[1] - 1]
                else:
                    newEmptyCell = [emptyCellIndex[0], emptyCellIndex[1] + 1]
    
            currGrid[emptyCellIndex[1]][emptyCellIndex[0]] = currGrid[newEmptyCell[1]][newEmptyCell[0]]
            currGrid[newEmptyCell[1]][newEmptyCell[0]] = 0
            emptyCellIndex = newEmptyCell
            printGrid(currGrid)

        prevTl = [cx, cy]

        # filter out contours by non big enough

     
       
#        x, y, w, h = cv.boundingRect(approx)
 #       cutout = frame[y:y + h, x: x + w]
  #      cv.imshow('cutout', cutout)

        #draw corners
        corners = frame.copy()
    #    corners = cv.circle(corners, (x,y), radius=3, color=(0, 0, 255), thickness=-1)
    #    corners = cv.circle(corners, (x + w,y), radius=3, color=(0, 0, 255), thickness=-1)
     #   corners = cv.circle(corners, (x,y + h), radius=3, color=(0, 0, 255), thickness=-1)
     #   corners = cv.circle(corners, (x + w,y + h), radius=3, color=(0, 0, 255), thickness=-1)
        

        '''
        approxImg = frame.copy()
        cv.drawContours(approxImg, [approx], -1, (0, 0, 255), 3)
        cv.imshow('approx', approxImg)
        
        tl = (approx[0][0][0], approx[0][0][1])
        tr = (approx[1][0][0], approx[1][0][1])
        br = (approx[2][0][0], approx[2][0][1])
        bl = (approx[3][0][0], approx[3][0][1])
        
        cv.circle(corners, tl, radius=3, color=(0, 0, 255), thickness=-1)
        cv.circle(corners, tr, radius=3, color=(0, 0, 255), thickness=-1)
        cv.circle(corners, bl, radius=3, color=(0, 0, 255), thickness=-1)
        cv.circle(corners, br, radius=3, color=(0, 0, 255), thickness=-1)
        cv.imshow('corners', corners)
        
        initialPoints = np.float32([[tl[0], tl[1]], [tr[0], tr[1]], [br[0], br[1]], [bl[0], bl[1]]])
        finalPoints = np.float32([[0, 0], [599, 0], [599, 599], [0, 599]])

        matrix = cv.getPerspectiveTransform(initialPoints, finalPoints)
        result = cv.warpPerspective(frame, matrix, (600,600), cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT, borderValue=(0,0,0))

        cv.imshow('perspective', result)

        grid: list[list[int]] = GetGrid(minesweeper, result, gridSize)
        '''

    print('hello')

if __name__ == "__main__":
    main()