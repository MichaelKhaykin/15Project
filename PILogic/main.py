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

def main():

    cap = cv.VideoCapture(0)
    
    gridSize: int = 3
    grid: List[List[int]] = GetGrid("images/minesweeper.png", "images/stanshuffle.png", gridSize)
    print(grid)
    graphTesting(grid)

    while(True):
        # Capture frame-by-frame

        _, upsidedownframe = cap.read()
        frame: ndarray = cv.rotate(upsidedownframe, cv.ROTATE_180)
        

        # Display the resulting frame

        #Waits for a user input to quit the application
        imgray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, thresh = cv.threshold(imgray, 127, 255, 0)
        contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        cv.drawContours(frame, contours, -1, (0,255,0), 3)

        cv.imshow('video', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    print('hello')

if __name__ == "__main__":
    main()