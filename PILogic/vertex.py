from __future__ import annotations
from helpers import Swap
from helpers import dirs

from typing import List, Tuple

class vertex:
    GScore: float
    FScore: float
    Parent: vertex
    Neighbors: List[vertex]
    Value: List[List[int]]
    EmptySpot: Tuple[int, int]

    def __init__(self: vertex):
        self.GScore = float("inf")
        self.FScore = float("inf")
        self.Parent = None
        self.Neighbors = []
        self.Value = [[]]
        self.EmptySpot = (-1, -1)

    def __lt__(self: vertex, obj: vertex):
        return self.FScore < obj.FScore

    def __le__(self: vertex, obj: vertex):
        return self.FScore <= obj.FScore

    def __eq__(self: vertex, obj: vertex):
        if obj is None:
            return False
        
        return self.FScore == obj.FScore

    def __gt__(self: vertex, obj: vertex):
        return self.FScore > obj.FScore

    def __ge__(self: vertex, obj: vertex):
        return self.FScore >= obj.FScore

    def GenerateMoves(self: vertex, goal: List[List[int]]) -> bool:

        if self.Value == goal:
            return True

        size: int = len(self.Value)

        (y, x) = self.EmptySpot

        for dir in dirs:
            
            offsety = y + dir[0]
            offsetx = x + dir[1]

            if offsetx >= 0 and offsetx < size and offsety >= 0 and offsety < size:
                
                newV: vertex = vertex()
                newV.EmptySpot = (offsety, offsetx)
                
                newV.Value = list(map(list, self.Value))
                Swap(newV.Value, (y, x), newV.EmptySpot)

                self.Neighbors.append(newV)

        return False