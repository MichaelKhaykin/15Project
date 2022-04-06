#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

from states import plotterStates

from robot import XYZPlotter

import time
import socket

plotter = XYZPlotter()

state = plotterStates.Stopped

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#server.setblocking(0)
server.bind(('192.168.1.226', 5000))

data = ''
prevData = None
cell = None
x = -1
y = -1

movements = []
index = 0

while True:

    if state == plotterStates.Moving:
        [y, x] = movements[index]
        if plotter.moveToGridCell(x, y):
            state = plotterStates.Tap
    elif state == plotterStates.Tap:
        if plotter.Tap():
            state = plotterStates.UnTap
    elif state == plotterStates.UnTap:
        if plotter.UnTap():
            state = plotterStates.Stopped
    elif state == plotterStates.Stopped:
        plotter.stop()

        if index < len(movements) - 1:
            state = plotterStates.Moving
            index += 1
            continue

        try:
            data, _ = server.recvfrom(1000)
            pass
        except socket.error:
            continue

        if data == b'' or data == prevData:
            continue
        
        print(data)
        for i in range(0, len(data)):
            val = data[i]
            movements.append([int(val // 3), int(val % 3)])
        index = 0

        print(movements)
        prevData = data
        state = plotterStates.Moving
    
