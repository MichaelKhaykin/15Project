from robot import robot
from graph import graph
from vertex import vertex
import cv2 as cv
import numpy as np
import math
import socket
import select

from sre_constants import CATEGORY_UNI_DIGIT
from enums import trackerStates
from numpy import False_, True_, ndarray, true_divide
from typing import List, Dict


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
#(2, 1), (2, 2), (1, 2), (1, 1), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (1, 1), (1, 0), (0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]
    data = ''
    prevData = None
    rob: robot = robot(gridSize, cameraID, True)
    rob.state = trackerStates.Waiting

    while(True):

        rob.update(UDPServerSocket)
        
        #UDPServerSocket.sendto("m".encode('utf-8'), ('192.168.1.226', 5000))
        try:
            data, _ = UDPServerSocket.recvfrom(1)
        except socket.error:
            pass

        if data == '' or prevData == data:
            continue

        print(f'Data recieved {data}')

        if data == b'C':
            rob.state = trackerStates.Calibrating
        elif data == b'F':
            rob.state = trackerStates.Following
        elif data == b'M':
            rob.state = trackerStates.CalculateSolution
            print('calculating solution')
        
        
        prevData = data

    

if __name__ == "__main__":
    main()

    #[(2, 1), (2, 0), (1, 0), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (1, 1), (1, 2), (0, 2), (0, 1), (1, 1), (1, 0), (2, 0), (2, 1), (1, 1), (1, 2), (2, 2)]