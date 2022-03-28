from robot import robot
from graph import graph
from vertex import vertex
import cv2 as cv
import numpy as np
import math
import socket

from sre_constants import CATEGORY_UNI_DIGIT
from enums import trackerStates
from numpy import False_, ndarray
from typing import List, Dict


def graphTesting(startGrid: List[List[int]]):
    gridSize: int = len(startGrid)
    graph: graph = graph(gridSize, gridSize)

    #Get this from camera at some point
    startVertex: vertex = vertex()
    startVertex.Value = startGrid
    
    goalArr: list[list[int]] = [[(i + j * gridSize + 1) % (gridSize * gridSize) 
                                for i in range(0, gridSize)] for j in range(0, gridSize)]
    goalVertex: vertex = vertex()
    goalVertex.Value = goalArr
    
    path = graph.AStar(startVertex, goalVertex)
    print(len(path))

def main():

    gridSize: int = 3
    cameraID: int = 0

    localIP     = "192.168.1.126"
    localPort   = 5000
    
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setblocking(0)

    # Bind to address and ip
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening")

    data = ''

    rob: robot = robot(gridSize, cameraID, False)

    while(True):

        try:
            data, _ = UDPServerSocket.recvfrom(10000)
        except socket.error:
            pass
        
        if data == b'S':
            rob.state = trackerStates.Following
        elif data == b'U':
            rob.state = trackerStates.Solving

        rob.update()
    
    print('hello')

if __name__ == "__main__":
    main()