from __future__ import annotations
from vertex import vertex 
from collections import deque
from heapq import *
from hueristics import Hueristics
from typing import List, Tuple, Dict


class graph:

    Mapping: Dict[int, Tuple[int, int]]

    def __init__(self: graph, width: int, height: int):
        self.Mapping = {}

        for y in range(0, height):
            for x in range(0, width):
                key = y * width + x + 1
                self.Mapping[key] = (y, x)

    def AStar(self: graph, start: vertex, goal: vertex) -> deque[vertex]:
        
        Height: int = len(start.Value)
        Width: int = len(start.Value[Height - 1])

        #Mark empty spot
        for y in range(0, Height):
            for x in range(0, Width):

                if start.Value[y][x] == 0:
                    start.EmptySpot = (y, x)
                    y = Height
                    break
            
        start.GScore = 0
        start.FScore = Hueristics.ManhattanHueristic(start.Value, self.Mapping)

        heap = []
        heappush(heap, (start.FScore, start))

        visited = []
        
        while len(heap) != 0:
            
            current: vertex = heappop(heap)[1]
            
            if(current.GenerateMoves(goal.Value)):
                goal = current
                break
            
            for x in current.Neighbors:

                if x.Value in visited:
                    continue

                tentativeDistance: float = current.GScore + 1
                if tentativeDistance < x.GScore:
                    x.GScore = tentativeDistance
                    x.Parent = current
                    x.FScore = tentativeDistance + Hueristics.ManhattanHueristic(x.Value, self.Mapping)
                
                heappush(heap, (x.FScore, x))
                visited.append(x.Value)

        #connect
        path: List[vertex] = list()
        curr: vertex = goal

        while curr.Parent != None:
            path.append(curr)
            curr = curr.Parent
        
        path.append(curr)
        return path
