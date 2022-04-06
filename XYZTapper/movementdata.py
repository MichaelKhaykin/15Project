class MoveData:
    
    def __init__(self, power, degrees, timeout, motor, tolerance):
        self.power = power
        self.degrees = degrees
        self.timeout = timeout
        self.motor = motor
        self.tolerance = tolerance
    
    def move(self):
        self.motor.dc(-self.power if abs(self.angle()) > self.degrees else self.power)

    def stop(self):
        self.motor.dc(0)

    def angle(self):
        return self.motor.angle()

    def isFinished(self):
        return abs(abs(self.motor.angle()) - self.degrees) < self.tolerance
    