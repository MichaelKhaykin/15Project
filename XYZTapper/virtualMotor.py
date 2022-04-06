from pybricks.tools import wait, StopWatch, DataLog

class VMotor:
    
    def __init__(self, motors):
        self.motors = motors
        self.watch = None
        
    def dc(self, power):
        for x in self.motors:
            x.dc(power)

    def reset_angle(self, angle):
        for x in self.motors:
            x.reset_angle(angle)

    def angle(self):
        angle = 0
        for x in self.motors:
            angle += x.angle()
        return angle / len(self.motors)

    def dcForTime(self, power, duration):
        if self.watch == None:
            self.watch = StopWatch()

        if self.watch.time() / 1000 > duration:
            self.watch = None
            return True

        self.dc(power)
        return False