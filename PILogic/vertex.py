from __future__ import annotations
from helpers import Swap
from helpers import dirs

class Vertex:
    GScore: float
    FScore: float
    Parent: Vertex
    Neighbors: list[Vertex]
    Value: list[list[int]]
    EmptySpot: tuple[int, int]

    def __init__(self: Vertex):
        self.GScore = float("inf")
        self.FScore = float("inf")
        self.Parent = None
        self.Neighbors = []
        self.Value = [[]]
        self.EmptySpot = (-1, -1)

    def __lt__(self: Vertex, obj: Vertex):
        return self.FScore < obj.FScore

    def __le__(self: Vertex, obj: Vertex):
        return self.FScore <= obj.FScore

    def __eq__(self: Vertex, obj: Vertex):
        if obj is None:
            return False
        
        return self.FScore == obj.FScore

    def __gt__(self: Vertex, obj: Vertex):
        return self.FScore > obj.FScore

    def __ge__(self: Vertex, obj: Vertex):
        return self.FScore >= obj.FScore

    def GenerateMoves(self: Vertex, goal: list[list[int]]) -> bool:

        if self.Value == goal:
            return True

        size: int = len(self.Value)

        (y, x) = self.EmptySpot

        for dir in dirs:
            
            offsety = y + dir[0]
            offsetx = x + dir[1]

            if offsetx >= 0 and offsetx < size and offsety >= 0 and offsety < size:
                
                newV: Vertex = Vertex()
                newV.EmptySpot = (offsety, offsetx)
                
                newV.Value = list(map(list, self.Value))
                Swap(newV.Value, (y, x), newV.EmptySpot)

                self.Neighbors.append(newV)

        return False