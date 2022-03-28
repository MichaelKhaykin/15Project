import sys, pygame
from cv2 import split
from pygame import Surface, Color, Vector2
from board import board
from button import button

pygame.init()

black = 0, 0, 0
img = pygame.image.load("PythonVisualizer/cooldog.jpg")
img = pygame.transform.scale(img, [600, 600])

gameBoard: board = board(location = Vector2(50, 50), gridSize = 3, image = img, padding = 0, backColor = Color(0, 0, 0, 0), gameBoardBackColor = Color(128, 0, 128, 255))

elevation: int = 3
shuffleButton: button = button("Shuffle", 100, 30, Vector2(gameBoard.left(), gameBoard.bottom() + elevation * 2), elevation, pygame.font.Font(None, 30), gameBoard.shuffle)

screen = pygame.display.set_mode([700, 700])

clock = pygame.time.Clock()

while 1:

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        
    mp: tuple[int, int] = pygame.mouse.get_pos()
    mousePos = Vector2(mp[0], mp[1])

    screen.fill(black)
    gameBoard.update(mousePos)
    gameBoard.draw(screen)

    shuffleButton.draw(screen)

    pygame.display.update()
    clock.tick(60)