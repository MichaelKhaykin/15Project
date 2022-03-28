from pygame import Rect, Surface, Vector2

from helpers import LerpVector

class tile:
    value: int
    rect: Rect
    image: Surface
    visible: bool

    lerping: bool
    amount: float
    goal: Vector2
    start: Vector2
    step: float

    def __init__(self, value, pos, img, visible = True):
        self.value = value
        r = img.get_rect()
        self.rect = Rect(pos.x, pos.y, r.width, r.height)
        self.image = img
        self.visible = visible
        self.lerping = False

    def x(self):
        return self.rect.x

    def setx(self, x):
        self.rect.x = x

    def sety(self, y):
        self.rect.y = y
    
    def y(self):
        return self.rect.y

    def width(self):
        return self.rect.width

    def height(self):
        return self.rect.height

    def moveTo(self, end: Vector2, step: float):
        self.start = Vector2(self.x(), self.y())
        self.goal = end
        self.amount = 0
        self.step = step
        self.lerping = True

    def update(self):
        if not self.lerping: return

        lerpPos = LerpVector(self.start, self.goal, self.amount)
        self.setx(lerpPos.x)
        self.sety(lerpPos.y)
        self.amount += self.step

        if self.amount >= 1:
            self.lerping = False
            self.setx(self.goal.x)
            self.sety(self.goal.y)

        pass

    def draw(self, screen: Surface):
        if not self.visible: return
        screen.blit(self.image, self.rect)