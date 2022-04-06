from virtualMotor import VMotor
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from movementdata import MoveData

class XYZPlotter:
    
    def __init__(self):
        self.XAxisMotor = VMotor([Motor(Port.B, positive_direction = Direction.COUNTERCLOCKWISE, gears = [8, 16]), 
                                  Motor(Port.C, gears = [8, 16])])
        self.YAxisMotor = VMotor([Motor(Port.A, positive_direction = Direction.COUNTERCLOCKWISE, gears = [8, 16])])

        self.FingerMotor = VMotor([Motor(Port.D, gears = [8, 16])])

        self.HorizontalLimitSwitch = TouchSensor(Port.S4)
        self.VerticalLimitSwitch = TouchSensor(Port.S3)

        self.ResetXDirection()
        self.ResetYDirection()
        self.ResetFinger()

        infiniteTimeOut = 100000
        tolerance = 5 #degrees

        rightMostX = 570
        middle = 430
        leftMostX = 290

        self.cellToMovements = {
            (0, 0): [MoveData(75, rightMostX, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 0, infiniteTimeOut, self.YAxisMotor, tolerance)],
            (0, 1): [MoveData(75, middle, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 0, infiniteTimeOut, self.YAxisMotor, tolerance)],
            (0, 2): [MoveData(75, leftMostX, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 0, infiniteTimeOut, self.YAxisMotor, tolerance)],
           
            (1, 0): [MoveData(75, rightMostX, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 120, infiniteTimeOut, self.YAxisMotor, tolerance)],
            (1, 1): [MoveData(75, middle, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 120, infiniteTimeOut, self.YAxisMotor, tolerance)],
            (1, 2): [MoveData(75, leftMostX, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 120, infiniteTimeOut, self.YAxisMotor, tolerance)],
           
            (2, 0): [MoveData(75, rightMostX, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 230, infiniteTimeOut, self.YAxisMotor, tolerance)],
            (2, 1): [MoveData(75, middle, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 230, infiniteTimeOut, self.YAxisMotor, tolerance)],
            (2, 2): [MoveData(75, leftMostX, infiniteTimeOut, self.XAxisMotor, tolerance), MoveData(50, 230, infiniteTimeOut, self.YAxisMotor, tolerance)]
        }

    
    def moveToGridCell(self, x, y):
        movements = self.cellToMovements[(y, x)]

        Finished = True
        for moveData in movements:
            if moveData.isFinished():
                moveData.stop()
                continue
            moveData.move()
            Finished = False

        return Finished

    def ResetXDirection(self):
        self.XAxisMotor.dc(-100)
        while not self.HorizontalLimitSwitch.pressed():
            pass
        self.XAxisMotor.dc(0)
        self.XAxisMotor.reset_angle(0)

    def ResetYDirection(self):
        self.YAxisMotor.dc(-100)
        while not self.VerticalLimitSwitch.pressed():
            pass
        self.YAxisMotor.dc(0)
        self.YAxisMotor.reset_angle(0)

    def ResetFinger(self):
        while(not self.UnTap()):
            pass
        self.FingerMotor.dc(0)

    def Tap(self):
        return self.FingerMotor.dcForTime(-50, 0.3)

    def UnTap(self):
        return self.FingerMotor.dcForTime(70, 0.2)

    def stop(self):
        self.XAxisMotor.dc(0)
        self.YAxisMotor.dc(0)