import random
import pygame
from swap import swap
from tile import tile
from pygame import Color, Surface, Vector2
import numpy as np

class states:
    waiting = 0,
    manualmoving = 1,
    shuffling = 2,

class board:
    boardState: states
    tiles: list[list[tile]]
    gridSize: int
    cellSize: int
    intToVal: dict[int, tile]
    location: Vector2
    gameBoardBackColor: Color
    img: Surface
    
    shuffleMoves: list[swap]

    def __init__(self, location: Vector2, gridSize: int, image: Surface, padding: int, backColor: Color, gameBoardBackColor: Color):
        self.location = location
        self.gridSize = gridSize
        self.tiles = [[(i + j * gridSize + 1) % (gridSize * gridSize) 
                    for i in range(0, gridSize)] for j in range(0, gridSize)]
        self.intToVal = dict[int, tile]()
        
        self.shuffleMoves = []
        self.boardState = states.waiting

        parts: list[Surface] = self.split(image, gridSize)
        
        self.cellSize = image.get_width() // gridSize

        self.img: Surface = Surface((self.cellSize * gridSize, self.cellSize * gridSize))
        self.img.fill(gameBoardBackColor)

        self.gameBoardBackColor = gameBoardBackColor

        self.clickedX = -1
        self.clickedY = -1

        for y in range(0, gridSize):
            for x in range(0, gridSize):
                
                index: int = y * gridSize + x
                number: int = (index + 1) % (gridSize * gridSize)
                t: tile = tile(number, Vector2(x * self.cellSize, y * self.cellSize), parts[index], number != 0)
                
                self.tiles[y][x] = t
                self.intToVal[number] = t

    def split(self, img: Surface, size: int) -> list[Surface]:
        splitSize: int = img.get_width() // size
        parts: list[Surface] = []

        for y in range(0, size):
            for x in range(0, size):
                cut: Surface = Surface([splitSize, splitSize])
                cut.blit(img, (0, 0), (x * splitSize, y * splitSize, splitSize, splitSize))
                parts.append(cut)
        return parts

    def update(self, mousePos: Vector2):
        
        for y in range(0, self.gridSize):
                for x in range(0, self.gridSize):
                    self.tiles[y][x].update()

        if self.boardState == states.waiting:
            
            leftClicked = pygame.mouse.get_pressed()[0]
            if not leftClicked: return

            localMouse = Vector2(mousePos.x - self.location.x, mousePos.y - self.location.y)

            for y in range(0, self.gridSize):
                for x in range(0, self.gridSize):
                    if self.tiles[y][x].rect.collidepoint(localMouse):
                        self.boardState = states.manualmoving
                        self.clickedX = x
                        self.clickedY = y

        elif self.boardState == states.manualmoving:
            
            (emptyY, emptyX) = self.getEmpty(self.clickedX, self.clickedY)

            if emptyX == -1 and emptyY == -1:
                self.boardState = states.waiting
                return

            self.shuffleMoves = [swap(self.clickedX, self.clickedY, emptyX, emptyY)]
            self.boardState = states.shuffling
            return

        elif self.boardState == states.shuffling:
            anyMoving: bool = self.anyMoving()

            if len(self.shuffleMoves) == 0 and not anyMoving:
                self.boardState = states.waiting
                return
            if not anyMoving:
                curSwap = self.shuffleMoves.pop(0)
                self.swapTile(curSwap, 0.1)

   

    def getEmpty(self, gridX: int, gridY: int):
        if gridY - 1 >= 0 and self.tiles[gridY - 1][gridX].value == 0: return (gridY - 1, gridX)
        if gridY + 1 < self.gridSize and self.tiles[gridY + 1][gridX].value == 0: return (gridY + 1, gridX)
        if gridX - 1 >= 0 and self.tiles[gridY][gridX - 1].value == 0: return (gridY, gridX - 1)
        if gridX + 1 < self.gridSize and self.tiles[gridY][gridX + 1].value == 0: return (gridY, gridX + 1)
        
        return (-1, -1)

    def width(self):
        return self.gridSize * self.cellSize
    
    def height(self):
        return self.gridSize * self.cellSize

    def bottom(self):
        return self.location.y + self.height()
    def left(self):
        return self.location.x

    def draw(self, screen: Surface):
        
        self.img.fill(self.gameBoardBackColor)

        for x in range(0, self.gridSize):
            for y in range(0, self.gridSize):
                t: tile = self.tiles[y][x]
                t.draw(self.img)
        
        screen.blit(self.img, (self.location.x, self.location.y))

    def getShuffleMoves(self, iterations: int):
        
        def neighbors(self, x: int, y: int):
            tiles: list[tuple[int, int]] = []
            if x - 1 >= 0: tiles.append((y, x - 1))
            if y - 1 >= 0: tiles.append((y - 1, x))
            if x + 1 < self.gridSize: tiles.append((y, x + 1))
            if y + 1 < self.gridSize: tiles.append((y + 1, x))
            return tiles

        swaps: list[swap] = []
        lastEmpty: tuple[int, int] = [-1, -1]
        emptyTile: tile = list(filter(lambda x: x.value == 0, np.hstack(self.tiles)))[0]
        empty: tuple[int, int] = [int(emptyTile.y() // self.cellSize), int(emptyTile.x() // self.cellSize)]

        for i in range(0, iterations):
            neighboringTiles: list[tuple[int, int]] = neighbors(self, empty[1], empty[0])
            newEmptyPos: tuple[int, int] = random.choice(neighboringTiles)
            while newEmptyPos == lastEmpty:
                newEmptyPos = random.choice(neighboringTiles)
            swaps.append(swap(newEmptyPos[1], newEmptyPos[0], empty[1], empty[0]))
            lastEmpty = empty
            empty = newEmptyPos

        return swaps

    def shuffle(self):
        self.shuffleMoves = self.getShuffleMoves(20)
        self.boardState = states.shuffling
        
    def swapTile(self, swapData: swap, step: float):

        self.tiles[swapData.sy][swapData.sx].moveTo(Vector2(self.tiles[swapData.ey][swapData.ex].x(), 
                                                            self.tiles[swapData.ey][swapData.ex].y()), step)

        self.tiles[swapData.ey][swapData.ex].setx(self.tiles[swapData.sy][swapData.sx].x())
        self.tiles[swapData.ey][swapData.ex].sety(self.tiles[swapData.sy][swapData.sx].y())

        save: tile = self.tiles[swapData.sy][swapData.sx]
        self.tiles[swapData.sy][swapData.sx] = self.tiles[swapData.ey][swapData.ex]
        self.tiles[swapData.ey][swapData.ex] = save


    def anyMoving(self):
        for y in range(0, self.gridSize):
            for x in range(0, self.gridSize):
                if self.tiles[y][x].lerping:
                    return True
        return False    