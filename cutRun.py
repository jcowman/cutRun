#Temporary name: Cut and Run
#Project for Mini LD 59: Swap
#by Joe Cowman (In progress)

import pygame
from pygame.locals import *
from sys import exit

SCREENX, SCREENY = (1080,720)
GAMEX,GAMEY = (320,208)
GRIDSIZE = 16

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

def get_spritesheet(filename):
    sheet = pygame.image.load(filename).convert_alpha()
    return sheet

def get_sprites(surf,step):
    w,h = surf.get_size()
    numX,numY = (w/step,h/step)
    x,y = (0,0)
    surfList = []

    for t in xrange(numX*numY):
        s = pygame.Surface((step,step),0,32)
        s.fill((1,1,1))
        s.set_colorkey((1,1,1))
        surfList.append(s)

    for r in xrange(numY):
        y= r*step
        
        for c in xrange(numX):
            x = c*step
            surfList[c+r*numX].blit(surf,(0,0),(c*step,r*step,step,step))

    return surfList

def demo_sprites(spriteList,destSurf,step):
    w,h = destSurf.get_size()
    numX = w/step
    x,y = (0,0)
    
    for s in spriteList:
        if x/step > numX:
            x = 0
            y += step

        destSurf.blit(s,(x,y))

        x += step

    return destSurf
        

sheet1 = get_spritesheet("example1.png")
list1 = get_sprites(sheet1,GRIDSIZE)
sheet2 = get_spritesheet("randomImage.png")
list2 = get_sprites(sheet2,GRIDSIZE)

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    gameSurf.fill(GRAY1)

    gameSurf = demo_sprites(list2,gameSurf,GRIDSIZE)
    #gameSurf.blit(list1[1],(0,0))
    #gameSurf.blit(sheet1,(0,0),(16, 80, 16, 16))

    if (SCREENX,SCREENY) != (GAMEX,GAMEY):
        pygame.transform.scale(gameSurf,(SCREENX,SCREENY),DISPLAYSURF)
    else:
        DISPLAYSURF.blit(gameSurf,(0,0))
        
    pygame.display.update()
