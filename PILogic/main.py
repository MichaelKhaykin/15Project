from tkinter import Frame
import cv2 as cv
import numpy as np
from numpy import ndarray
from graph import Graph
from vertex import Vertex
from typing import List

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

def GetGrid(ogImgName: str, unsortedImgName: str, gridSize: int) -> List[List[int]]:
    
    ogImg: ndarray = cv.imread(ogImgName)
    ogImgCuts: list[ndarray] = SplitImage(ogImg, gridSize)
   
    unsortedImg: ndarray = cv.imread(unsortedImgName)
    unsortedCuts: list[ndarray] = SplitImage(unsortedImg, gridSize)

    calculatedGrid: list[list[int]] =  [[0 for i in range(3)] for j in range(3)]
    
    for i in range(0, len(ogImgCuts) - 1):

        for j in range(0, len(unsortedCuts)):

            difference: ndarray = cv.subtract(ogImgCuts[i], unsortedCuts[j])    
            result: bool = not np.any(difference)
            if result:
                cv.putText(unsortedCuts[j], f"{i + 1}", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv.LINE_AA)

                x: int = j % gridSize
                y: int = j // gridSize

                calculatedGrid[y][x] = i + 1
                break
    
    return calculatedGrid

def nothing():
    pass

def HSVTesting():
    #Minimum value of a trackbar is always zero, first number represents start pos
    cv.createTrackbar('Min H','inrange',114,180, nothing)
    cv.createTrackbar('Min S','inrange',124,255, nothing)
    cv.createTrackbar('Min V','inrange',48,255, nothing)
    
    cv.createTrackbar('Max H','inrange',169,180, nothing)
    cv.createTrackbar('Max S','inrange',255,255, nothing)
    cv.createTrackbar('Max V','inrange',150,255, nothing)

def MinH() -> int:
    return cv.getTrackbarPos('Min H', 'inrange')
def MinS() -> int:
    return cv.getTrackbarPos('Min S', 'inrange')
def MinV() -> int:
    return cv.getTrackbarPos('Min V', 'inrange')
def MaxH() -> int:
    return cv.getTrackbarPos('Max H', 'inrange')
def MaxS() -> int:
    return cv.getTrackbarPos('Max S', 'inrange')
def MaxV() -> int:
    return cv.getTrackbarPos('Max V', 'inrange')

def main():

    cv.namedWindow('inrange')
    HSVTesting()

    cap = cv.VideoCapture(0)
    
    gridSize: int = 3
    grid: List[List[int]] = GetGrid("images/minesweeper.png", "images/stanshuffle.png", gridSize)
    print(grid)
    graphTesting(grid)

    while(True):
        # Capture frame-by-frame

        _, upsidedownframe = cap.read()
        frame: ndarray = cv.rotate(upsidedownframe, cv.ROTATE_180)
        
        blur = cv.GaussianBlur(frame,(5,5),0)

        hsv: ndarray = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
        purple_lowerBound = np.array([MinH(), MinS(), MinV()])
        purple_upperBound = np.array([MaxH(), MaxS(), MaxV()])
        inrange = cv.inRange(hsv, purple_lowerBound, purple_upperBound)

        cv.imshow('inrange', inrange)

        canny = cv.Canny(inrange, 100, 200)
        cv.imshow('canny', canny)

        contours, hierarchy = cv.findContours(canny, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contourImg = frame.copy()
        cv.drawContours(contourImg, contours, -1, (0,255,0), 3)

        cv.imshow('contour', contourImg)

        
        # filter out contours by non big enough

        absminarea = 500
        contours = list(filter(lambda x: cv.contourArea(x) > absminarea, contours))
        
        if(len(contours) == 0):
            continue
        
        cnt = contours[0]
        min_area = cv.contourArea(cnt)

        for cont in contours:
            contArea = cv.contourArea(cont)
            if contArea < min_area:
                cnt = cont
                min_area = cv.contourArea(cont)

        perimeter = cv.arcLength(cnt,True)
        epsilon = 0.01*cv.arcLength(cnt,True)
        approx = cv.approxPolyDP(cnt,epsilon,True)
       
#        x, y, w, h = cv.boundingRect(approx)
 #       cutout = frame[y:y + h, x: x + w]
  #      cv.imshow('cutout', cutout)

        #draw corners
        corners = frame.copy()
    #    corners = cv.circle(corners, (x,y), radius=3, color=(0, 0, 255), thickness=-1)
    #    corners = cv.circle(corners, (x + w,y), radius=3, color=(0, 0, 255), thickness=-1)
     #   corners = cv.circle(corners, (x,y + h), radius=3, color=(0, 0, 255), thickness=-1)
     #   corners = cv.circle(corners, (x + w,y + h), radius=3, color=(0, 0, 255), thickness=-1)
      

        approxImg = frame.copy()
        cv.drawContours(approxImg, [approx], -1, (0, 0, 255), 3)
        cv.imshow('approx', approxImg)
        
        tl = (approx[0][0], approx[0][1]) #fix this
        tr = (approx[1][0], approx[1][1])
        bl = (approx[2][0], approx[2][1])
        br = (approx[3][0], approx[3][1])

        
        cv.circle(corners, tl, radius=3, color=(0, 0, 255), thickness=-1)
        cv.circle(corners, tr, radius=3, color=(0, 0, 255), thickness=-1)
        cv.circle(corners, bl, radius=3, color=(0, 0, 255), thickness=-1)
        cv.circle(corners, br, radius=3, color=(0, 0, 255), thickness=-1)
        cv.imshow('corners', corners)
        #initialPoints = np.float32([[x, y], [x + w - 1, y], [x + w - 1, y + h - 1], [x, y + h - 1]])
        #finalPoints = np.float32([[0, 0], [599, 0], [599, 599], [0, 599]])

        #matrix = cv.getPerspectiveTransform(initialPoints, finalPoints)
        #result = cv.warpPerspective(frame, matrix, (600,600), cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT, borderValue=(0,0,0))

        #cv.imshow('perspective', result)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    print('hello')

if __name__ == "__main__":
    main()