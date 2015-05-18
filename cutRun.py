#Temporary name: Cut and Run
#Project for Mini LD 59: Swap
#May 2015
#by Joe Cowman (In progress)

import pygame
from pygame.locals import *
from sys import exit
import random
import math

import landforms #made by me

SCREENX, SCREENY = (1080,720)
GAMEX,GAMEY = (320,208)
GRIDX,GRIDY = (19,12) #For coordinates
GRIDSIZE = 16

GRAVCONSTANT = 0.08 #tiles/s^2

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY1 = (125,125,125)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
LIGHTBLUE = (100,255,255)
COLORKEY = (1,1,1)

IDLE = "Idle"
LEFTRUN = "LeftRun"
LEFTFACE = "LeftFace"
RIGHTRUN = "RightRun"
RIGHTFACE = "RightFace"

UP = "Up"
RIGHT = "Right"
DOWN = "Down"
LEFT = "Left"

pygame.init()

DISPLAYSURF = pygame.display.set_mode((SCREENX,SCREENY))

pygame.display.set_caption("CODENAME: Cut and Run")

global gameSurf
gameSurf = pygame.Surface((GAMEX,GAMEY))

gameGrid = {}

for x in xrange(GRIDX+1):
    for y in xrange(GRIDY+1):
        gameGrid[(x,y)] = 0
        

TILEINDEX = {"a":32,"b":33,"c":34,"d":35,"e":36,"f":37,"g":38,"h":39,"i":40,"j":41,"k":42,"l":43,"m":44,"n":45,"o":46,"p":47,"q":48,"r":49,"s":50,"t":51,"u":52,"v":53,"w":54,"x":55,"y":56,"z":57,"1":58,"2":59,"3":60,"4":61,"5":62,"6":63}

#sprite ranges for each animated character
P1o,P1 = (0,9)
P2o,P2 = (9,18)
P3o,P3 = (18,27)

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

class Landform(object):

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
        self.rectDict = {}

        for t in self.typeList:
            if t != "0":
                self.typeDict[t] = self.spriteList[TILEINDEX[t]]
                self.rectDict[t] = self.typeDict[t].get_bounding_rect()

        self.surf = self.render_surf()

        self.gridCoords = gridCoords
        self.gridX,self.gridY = gridCoords

    def update_grid(self,globalGrid,step=GRIDSIZE):

        for row in xrange(len(self.terrain)):
            
            for column in xrange(len(self.terrain[row])):
                
                if self.terrain[row][column] != "0":
                    
                    boundRect = Rect(self.rectDict[self.terrain[row][column]])
                    boundRect.x += step*(self.gridX+column)
                    boundRect.y += step*(self.gridY+row)
                    
                    globalGrid[(self.gridX+column,self.gridY+row)]=boundRect

        return globalGrid

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

class Anisprite(object):

    #aniSpeed in ms
    #moveSpeed and jumpPower in pixels/s

    def __init__(self,spriteSlice,initGridCoords,moveSpeed=0,jumpPower=0,allowFloat=False,aniSpeed=80,step=GRIDSIZE):
        
        self.spriteList = spriteSlice[:] + [pygame.transform.flip(x,True,False) for x in spriteSlice[3:6]]
        
        self.coords = initGridCoords[0]*step,initGridCoords[1]*step
        self.x,self.y = self.coords
        
        self.state = IDLE
        self.spriteIndex = 0

        self.aniSpeed = aniSpeed
        self.timeSinceAni = 0

        self.moveSpeed = moveSpeed
        self.jumpPower = jumpPower

        self.vx, self.vy = (0,0)

        self.boundRects = [r.get_bounding_rect() for r in self.spriteList]
        self.boundBox = (0,0,0,0)

        if not allowFloat:

            for r in xrange(len(self.boundRects)):
                
                bot = self.boundRects[r].bottom
                
                if bot != 16:
                    
                    mis = 16 - bot

                    tempSurf = pygame.Surface((16,16),0,32)
                    tempSurf.fill(COLORKEY)
                    tempSurf.blit(self.spriteList[r],(0,mis))
                    
                    self.spriteList[r].fill(COLORKEY)
                    self.spriteList[r].blit(tempSurf,(0,0))

                    self.boundRects[r].bottom = 16

        self.gridRect = Rect(0,0,0,0)
        self.gridCoords = []

        self.onSolidGround = True

    def jump(self,boost=0):
        
        if self.onSolidGround:
            self.vy -= (self.jumpPower+boost)
            self.onSolidGround = False

    def changeState(self,newState=None):

        self.timeSinceAni = 0

        if newState == IDLE:
            self.state = IDLE
            self.spriteIndex = 0

        elif newState == LEFTFACE:
            self.state = LEFTFACE
            self.spriteIndex = 9

        elif newState == LEFTRUN:
            self.state = LEFTRUN
            self.spriteIndex = 9

        elif newState == RIGHTFACE:
            self.state = RIGHTFACE
            self.spriteIndex = 3

        elif newState == RIGHTRUN:
            self.state = RIGHTRUN
            self.spriteIndex = 3

    def check_col(self,tile_coord,tiles=gameGrid):

        direction = None
        yDist = 0

        tile_rect = tiles[tile_coord]

        if tile_rect:

            if self.boundBox.colliderect(tile_rect):

##                xDist = abs(self.boundBox.centerx**2 + tile_rect.centerx**2)
##                yDist = abs(self.boundBox.centery**2 + tile_rect.centery**2)
##
##                if xDist > yDist:
##
##                    if self.boundBox.centerx < tile_rect.centerx:
##                        direction = RIGHT
##
##                    else:
##                        direction = LEFT
##
##                elif yDist > xDist:
##
##                    if self.boundBox.centery < tile_rect.centery:
##                        direction = DOWN
##
##                    else:
##                        direction = UP

                xDist = abs(self.boundBox.centerx - tile_rect.centerx)
                yDist = abs(self.boundBox.centery - tile_rect.centery)

                if xDist > yDist:

                    if self.boundBox.centerx < tile_rect.centerx:
                        direction = RIGHT

                    else:
                        direction = LEFT

                elif yDist > xDist:

                    if self.boundBox.centery < tile_rect.centery:
                        direction = DOWN

                    else:
                        direction = UP


        return direction

    def update(self,msPassed,step=GRIDSIZE,screenDim=(GAMEX,GAMEY),gridDim=(GRIDX,GRIDY),globalGrid=gameGrid):

        self.timeSinceAni += msPassed

        if self.state == IDLE:
            self.vx = 0

        if self.state == LEFTRUN:

            if self.timeSinceAni >= self.aniSpeed:
                
                self.timeSinceAni = 0
                self.spriteIndex += 1

                if self.spriteIndex > 11:
                    self.spriteIndex = 9

            self.vx = -self.moveSpeed

        if self.state == RIGHTRUN:

            if self.timeSinceAni >= self.aniSpeed:
                
                self.timeSinceAni = 0
                self.spriteIndex += 1

                if self.spriteIndex > 5:
                    self.spriteIndex = 3

            self.vx = self.moveSpeed

##        if not self.onSolidGround:
##            #self.vy += float(GRAVCONSTANT*step)/msPassed**2
##            self.vy += float(GRAVCONSTANT*step)
##        else:
##            self.vy = 0

        self.vy += float(GRAVCONSTANT*step)

        #print self.vy,self.y

        self.x += self.vx*(msPassed/1000.0)
        self.y += self.vy*(msPassed/1000.0)

        #print self.vy,self.y

        self.coords = (self.x,self.y)

        self.boundBox = Rect(self.boundRects[self.spriteIndex])
        
        self.boundBox.x += self.x
        self.boundBox.y += self.y

        x1,x2 = int(self.x),self.boundBox.right-1
        y1,y2 = int(self.y),self.boundBox.bottom-1
        
        screenX,screenY = screenDim
        gridX,gridY = gridDim

        xGrids = [x1/step,x2/step]
        yGrids = [y1/step,y2/step]

        self.currentGrid = [(xGrids[0],yGrids[0]),(xGrids[1],yGrids[0]),(xGrids[0],yGrids[1]),(xGrids[1],yGrids[1])]
        self.gridRect = Rect(xGrids[0],yGrids[0],xGrids[1]-xGrids[0],yGrids[1]-yGrids[0])

        if self.currentGrid[0] == self.currentGrid[1]:
            del self.currentGrid[0]

        if self.currentGrid[-1] == self.currentGrid[-2]:
            del self.currentGrid[-1]

        ##COLLISION DETECTION ZONE##

##        if globalGrid[self.gridRect.topright]:
##            self.x -= (self.boundBox.right - self.gridRect.right*step)
##
##        else:
##
##            if globalGrid[self.gridRect.bottomleft] or globalGrid[self.gridRect.bottomright]:
##                self.onSolidGround = True
##                self.y = self.gridRect.top*step
##            else:
##                self.onSolidGround = False

        #print timePassed,self.vy

        for t in self.currentGrid:

            #print "hi"

            try:
            
                colDirection = self.check_col(t)

            except:
                print self.currentGrid, self.boundBox, self.coords, timePassed

            if colDirection:

                foot = self.boundBox.bottom
                #print foot, foot%step

            
                if colDirection == DOWN:
                    self.onSolidGround = True
                    tileY = int(self.y/step)
                    #print tileY
                    self.y = tileY*step
                    self.vy = 0

            

            


        

        #Check Below

        ##END ZONE##

        self.coords = (self.x,self.y)
                
    def draw(self,destSurf):

        destSurf.fill(RED,self.boundBox)
        
        destSurf.blit(self.spriteList[self.spriteIndex],self.coords)
        
        return destSurf
        

sheet1 = get_spritesheet("example1.png")
list1 = get_sprites(sheet1,GRIDSIZE)
sheet2 = get_spritesheet("randomImage.png")
list2 = get_sprites(sheet2,GRIDSIZE)
sheet3 = get_spritesheet("numbered.png")
list3 = get_sprites(sheet3,GRIDSIZE)
sheet4 = get_spritesheet("alt2.png")
list4 = get_sprites(sheet4,GRIDSIZE)

landList = []

for x in [0,5,10,15]:
    landList.append(Landform(landforms.base5x3,list1,(x,10)))

landList.append(Landform(landforms.stair6x6,list1,(14,4)))

for l in landList:
    gameGrid = l.update_grid(gameGrid)

#land1 = Landform(landforms.base5x3,list1,(0,10))
#land2 = Landform(landforms.stair6x6,list1,(5,10))

#player = Anisprite(list4[P2o:P2],(0,9),90,90,True)
player = Anisprite(list1[P3o:P3],(0,9),90,200,False)

aniList = [player]

clock = pygame.time.Clock()
timePassed = clock.tick()
timePassedSeconds = timePassed/1000.

while True:

    for event in pygame.event.get():
        
        if event.type == QUIT:
            exit()

        elif event.type == KEYDOWN:

            if event.key == K_LEFT:
                player.changeState(LEFTRUN)

            if event.key == K_RIGHT:
                player.changeState(RIGHTRUN)

            if event.key == K_SPACE:
                player.jump()

        elif event.type == KEYUP:

            if event.key == K_LEFT:
                if player.state == LEFTRUN:
                    player.changeState(IDLE)

            if event.key == K_RIGHT:
                if player.state == RIGHTRUN:
                    player.changeState(IDLE)

    gameSurf.fill(LIGHTBLUE)

    gameSurf = draw_grid(gameSurf,GRIDSIZE)

    #gameSurf = demo_sprites(list1,gameSurf,GRIDSIZE)
    #gameSurf.blit(list3[tileIndex[random.choice(TILEINDEX.keys())]],(0,0))
    #gameSurf.blit(list1[1],(0,0))
    #gameSurf.blit(sheet1,(0,0),(16, 80, 16, 16))

    #gameSurf = land1.blit_surf(gameSurf)

    for x in landList:
        gameSurf = x.blit_surf(gameSurf)
    #gameSurf = land2.blit_surf(gameSurf)

    for a in aniList:
        a.update(timePassed)
        gameSurf = a.draw(gameSurf)

    if (SCREENX,SCREENY) != (GAMEX,GAMEY):
        pygame.transform.scale(gameSurf,(SCREENX,SCREENY),DISPLAYSURF)
    else:
        DISPLAYSURF.blit(gameSurf,(0,0))
        
    pygame.display.update()

    timePassed = clock.tick()
    timePassedSeconds = timePassed/1000.
