#Temporary name: Cut and Run
#Project for Mini LD 59: Swap
#by Joe Cowman (In progress)

import pygame
from pygame.locals import *
from sys import exit

SCREENX, SCREENY = (1080,720)
GAMEX,GAMEY = (1080,720)

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY1 = (125,125,125)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

pygame.init()

DISPLAYSURF = pygame.display.set_mode((SCREENX,SCREENY))

global gameSurf
gameSurf = pygame.Surface((GAMEX,GAMEY))

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    gameSurf.fill(GRAY1)

    if (SCREENX,SCREENY) != (GAMEX,GAMEY):
        pygame.transform.scale(gameSurf,(SCREENX,SCREENY),DISPLAYSURF)
    else:
        DISPLAYSURF.blit(gameSurf,(0,0))
        
    pygame.display.update()
