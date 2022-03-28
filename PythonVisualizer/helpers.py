from pygame import Vector2


def LerpFloat(a: float, b: float, amount: float):
    return a + amount * (b - a)

def LerpVector(a: Vector2, b: Vector2, amount: float):
    return Vector2(LerpFloat(a.x, b.x, amount), LerpFloat(a.y, b.y, amount))