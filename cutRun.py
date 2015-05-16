#Temporary name: Cut and Run
#Project for Mini LD 59: Swap
#May 2015
#by Joe Cowman (In progress)

import pygame
from pygame.locals import *
from sys import exit
import random
import landforms #made by me

SCREENX, SCREENY = (1080,720)
GAMEX,GAMEY = (320,208)
GRIDX,GRIDY = (19,12) #For coordinates
GRIDSIZE = 16

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY1 = (125,125,125)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
COLORKEY = (1,1,1)

pygame.init()

DISPLAYSURF = pygame.display.set_mode((SCREENX,SCREENY))

global gameSurf
gameSurf = pygame.Surface((GAMEX,GAMEY))

TILEINDEX = {"a":32,"b":33,"c":34,"d":35,"e":36,"f":37,"g":38,"h":39,"i":40,"j":41,"k":42,"l":43,"m":44,"n":45,"o":46,"p":47,"q":48,"r":49,"s":50,"t":51,"u":52,"v":53,"w":54,"x":55,"y":56,"z":57,"1":58,"2":59,"3":60,"4":61,"5":62,"6":63}

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
        s.fill(COLORKEY)
        s.set_colorkey(COLORKEY)
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

def draw_grid(surf,step,width=1,color=WHITE):
    w,h = surf.get_size()
    numX,numY = (w/step,h/step)
    x,y = (0,0)

    for c in xrange(numX):
        x = c*step
        pygame.draw.line(surf,color,(x,0),(x,h),width)

    for r in xrange(numY):
        y = r*step
        pygame.draw.line(surf,color,(0,y),(w,y),width)

    return surf

class landform(object):

    def __init__(self,terrain,spriteList,gridCoords):

        self.terrain = terrain[:]
        self.spriteList = spriteList
        self.numX = len(max(self.terrain,key=len))
        self.numY = len(self.terrain)

        self.typeList = []

        for s in self.terrain:
            for c in s:
                if c not in self.typeList:
                    self.typeList.append(c)

        self.typeDict = {}

        for t in self.typeList:
            if t != "0":
                self.typeDict[t] = self.spriteList[TILEINDEX[t]]

        self.surf = self.render_surf()

        self.gridCoords = gridCoords
        self.gridX,self.gridY = gridCoords

    def render_surf(self,step=GRIDSIZE):
        
        w = self.numX*step
        h = self.numY*step
        x,y = (0,0)

        surf = pygame.Surface((w,h),0,32)
        surf.fill(COLORKEY)
        surf.set_colorkey(COLORKEY)

        for r in self.terrain:
            
            for c in r:
                if c != "0":
                    surf.blit(self.typeDict[c],(x,y))
                x+= step

            x = 0
            y += step

        return surf

    def blit_surf(self,destSurf,step=GRIDSIZE):
        
        self.globalX,self.globalY = self.gridX*step,self.gridY*step
        
        destSurf.blit(self.surf,(self.globalX,self.globalY))

        return destSurf
        

sheet1 = get_spritesheet("example1.png")
list1 = get_sprites(sheet1,GRIDSIZE)
sheet2 = get_spritesheet("randomImage.png")
list2 = get_sprites(sheet2,GRIDSIZE)
sheet3 = get_spritesheet("numbered.png")
list3 = get_sprites(sheet3,GRIDSIZE)

landList = []

for x in [0,5,10,15]:
    landList.append(landform(landforms.base5x3,list1,(x,10)))

landList.append(landform(landforms.stair6x6,list1,(14,4)))

land1 = landform(landforms.base5x3,list1,(0,10))
land2 = landform(landforms.stair6x6,list1,(5,10))

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    gameSurf.fill(GRAY1)

    gameSurf = draw_grid(gameSurf,GRIDSIZE)

    #gameSurf = demo_sprites(list1,gameSurf,GRIDSIZE)
    #gameSurf.blit(list3[tileIndex[random.choice(TILEINDEX.keys())]],(0,0))
    #gameSurf.blit(list1[1],(0,0))
    #gameSurf.blit(sheet1,(0,0),(16, 80, 16, 16))

    #gameSurf = land1.blit_surf(gameSurf)

    for x in landList:
        gameSurf = x.blit_surf(gameSurf)
    #gameSurf = land2.blit_surf(gameSurf)

    if (SCREENX,SCREENY) != (GAMEX,GAMEY):
        pygame.transform.scale(gameSurf,(SCREENX,SCREENY),DISPLAYSURF)
    else:
        DISPLAYSURF.blit(gameSurf,(0,0))
        
    pygame.display.update()
