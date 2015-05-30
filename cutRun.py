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

FPS = 60

SCREENX, SCREENY = (1080,720)
GAMEX,GAMEY = (320,208)
GRIDX,GRIDY = (19,12) #For coordinates, so there are actually 1 more of each tile
GRIDSIZE = 16

GRAVCONSTANT = 20 #tiles/s^2
GRIDSPEED = 0.5 #sec/shift

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

global PLAYEROFFSETX
PLAYEROFFSETX = 0

CHANGETILEEVENT = USEREVENT + 1

TILEINDEX = {"a":32,"b":33,"c":34,"d":35,"e":36,"f":37,"g":38,"h":39,"i":40,"j":41,"k":42,"l":43,"m":44,"n":45,"o":46,"p":47,"q":48,"r":49,"s":50,"t":51,"u":52,"v":53,"w":54,"x":55,"y":56,"z":57,"1":58,"2":59,"3":60,"4":61,"5":62,"6":63}
TERRAINLISTS = [["b","a","c","d","e","f","g","h"],["j","i","k","l","m","n","o","p"],["q","r","s","t"],["u","v","w","x"],["y","z"],["1","2","3","4","5"],["6"]]

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

    def change_grid(self,x=0,y=0):
        self.gridX += x
        self.gridY += y
        self.gridCoords = (self.gridX,self.gridY)

    def update_grid(self,globalGrid,step=GRIDSIZE):

        for row in xrange(len(self.terrain)):
            
            for column in xrange(len(self.terrain[row])):

                terrainIndex = self.terrain[row][column]
                
                if terrainIndex != "0":
                    
                    boundRect = Rect(self.rectDict[self.terrain[row][column]])
                    boundRect.x += step*(self.gridX+column)
                    boundRect.y += step*(self.gridY+row)

                    tileSurf = self.typeDict[terrainIndex]
                    
                    globalGrid[(self.gridX+column,self.gridY+row)]=(boundRect,tileSurf)

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

    def blit_surf(self,destSurf,xOffset=0,step=GRIDSIZE):
        
        self.globalX,self.globalY = self.gridX*step+xOffset,self.gridY*step
        
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
        self.currentCollide = None

    def changePos(self,deltaX=0,deltaY=0):
        self.x += deltaX
        self.y += deltaY

        self.coords = (self.x,self.y)
        #self.boundBox

    def jump(self,boost=0):
        
        if self.onSolidGround:
            self.vy = -(self.jumpPower+boost)
            self.onSolidGround = False
            #print self.vy

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

        try:
            tile_rect = tiles[tile_coord][0]
        except TypeError:
            tile_rect = None

        if tile_rect:

            if self.boundBox.colliderect(tile_rect):

                xDist = abs(self.boundBox.centerx - tile_rect.centerx)
                yDist = abs(self.boundBox.centery - tile_rect.centery)

                if xDist > yDist:

                    if self.boundBox.centerx < tile_rect.centerx:
                        direction = RIGHT

                    else:
                        direction = LEFT

                elif yDist > xDist:

                    if self.boundBox.centery < tile_rect.centery:
                        
                        if tile_rect.collidepoint(self.boundBox.midbottom):
                            direction = DOWN

                    else:
                        
                        if tile_rect.collidepoint(self.boundBox.midtop):
                            direction = UP


        return direction

    def update(self,msPassed,step=GRIDSIZE,screenDim=(GAMEX,GAMEY),gridDim=(GRIDX,GRIDY),globalGrid=gameGrid):


        msPassed = min(msPassed,1000./FPS)

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

        self.vy += float(GRAVCONSTANT*step)*(msPassed/1000.0)

        self.x += self.vx*(msPassed/1000.0)
        self.y += self.vy*(msPassed/1000.0)

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

        for t in self.currentGrid:

            try:
                globalGrid[t]

            except:
                globalGrid[t] = 0

            try:
                colDirection = self.check_col(t)

            except:
                print self.currentGrid, self.boundBox, self.coords, timePassed

            if colDirection:


                tileBox = globalGrid[t][0]

                foot = self.boundBox.bottom

                self.currentCollide = colDirection

            
                if colDirection == DOWN:
                    tileY = int(self.y/step)
                    self.y = tileY*step
                    self.vy = 0
                    self.onSolidGround = True

                if colDirection == RIGHT:
                    tileX = int(self.x/step)
                    self.x = tileBox.left - self.boundBox.width - (step-self.boundBox.width)*0.5
                    self.vx = 0
                    self.onSolidGround = True

                if colDirection == UP:
                    tileY = int(self.y/step) + 1
                    self.vy = 0
                    self.y = tileBox.bottom - (step-self.boundBox.top%step)

                if colDirection == LEFT:
                    tileX = int(self.x/step) + 1
                    self.vx = 0
                    self.x = tileBox.right - (step-self.boundBox.width)*0.5
                    self.onSolidGround = True


        self.coords = (self.x,self.y)

        return self.vx*(msPassed/1000.0)
                
    def draw(self,destSurf):

        #destSurf.fill(RED,self.boundBox)
        
        destSurf.blit(self.spriteList[self.spriteIndex],self.coords)
        
        return destSurf

def pruneGrid(gameGrid,leftLimit,bottomLimit):

    for t in gameGrid.keys():
        
        x,y = t

        if x <= leftLimit:
            del gameGrid[t]

        if y >= bottomLimit:
            del gameGrid[t]

def genGround(segmentLength,noiseFactor,spriteLists,startY,startX):
    
    currentLength = 0
    dimList = []
    stringList = []
    terrainList = []

    lastY = startY #default

    while currentLength < segmentLength:

        #X Calculation

        x = 5 #default
        deltaX = 0

        deltaX = random.randint(-1,1)*random.randint(0,noiseFactor+int((random.random()**2)*random.randint(0,noiseFactor**2)))

        x += deltaX

        x = max(x,1)

        if x > 5:
            if random.randint(0,1):
                x = x/random.randint(1,x)

        if x + currentLength > segmentLength:
            x = segmentLength - currentLength

        currentLength += x

        y = lastY

        deltaY = int(random.randint(-1,1)*(random.random()*random.randint(0,y)+random.random()*random.randint(0,noiseFactor)))

        y += deltaY

        y = max(y,1)
        y = min(y,GRIDY-2)

        dimList.append((x,y))
        lastY =  y

    for d in dimList:

        s = []

        c = random.randint(1,50)

        if c > 1:
            n = random.randint(0,3)

            s = [random.choice(TERRAINLISTS[n])*d[0]]*d[1] #set terrain to default char

            for x in xrange(random.randint(0,d[0]*d[1])):
                if random.randint(0,noiseFactor**2)*0.5 > noiseFactor:
                    row = random.randint(0,len(s)-1)
                    index = random.randint(0,len(s[row])-1)
                    new = random.choice(TERRAINLISTS[n])

                    try:
                        s[row] = s[row][0:index] + new + s[row][index+1:]
                    except:
                        s[row] = s[row][:-1] + new

        else:
            n = random.randint(4,6)

            s = [random.choice(TERRAINLISTS[n])*d[0]]*d[1] #set terrain to default char

        stringList.append(s)

    possibleLists = [spriteLists[0]]
    otherLists = spriteLists[1:]

    for x in xrange(0,min(len(otherLists),random.randint(0,noiseFactor))):
        possibleLists.append(otherLists.pop(random.randint(0,len(otherLists)-1)))

    xStep = startX
    yFloor = GRIDY + 1
    
    for t in xrange(len(stringList)):

        terrainList.append(Landform(stringList[t],random.choice(possibleLists),(xStep,yFloor-dimList[t][1])))
        xStep += dimList[t][0]

    return terrainList


#"""
        

sheet1 = get_spritesheet("example1.png")
list1 = get_sprites(sheet1,GRIDSIZE)
sheet2 = get_spritesheet("randomImage.png")
list2 = get_sprites(sheet2,GRIDSIZE)
sheet3 = get_spritesheet("numbered.png")
list3 = get_sprites(sheet3,GRIDSIZE)
sheet4 = get_spritesheet("alt2.png")
list4 = get_sprites(sheet4,GRIDSIZE)

landList = []

#for x in xrange(10):
landList += genGround(1000,10,[list1,list2,list3,list4],3,0)

"""

for x in [0,5,10,15]:
    landList.append(Landform(landforms.base5x3,list1,(x,10)))

landList.append(Landform(landforms.stair6x6,list1,(14,4)))

landList.append(Landform(landforms.floatform,list1,(3,4)))

landList.append(Landform(landforms.plat3x1,list1,(9,7)))

landList.append(Landform(landforms.base5x3,list1,(19,5)))

#landList.append(Landform(["m"*100],list4,(20,4)))

"""

for l in landList:
    gameGrid = l.update_grid(gameGrid)


#land1 = Landform(landforms.base5x3,list1,(0,10))
#land2 = Landform(landforms.stair6x6,list1,(5,10))

#player = Anisprite(list4[P2o:P2],(0,9),90,200,True)
player = Anisprite(list1[P1o:P1],(0,9),90,206,False)

aniList = [player]

gridSpeed = GRIDSPEED
timeSinceGridShift = 0.

fillColor = (0,0,0)

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

            if event.key == K_RETURN: #debug key 1

##                for x in xrange(GRIDX+1):
##                    for y in xrange(GRIDY+1):
##                        gameGrid[(x,y)] = 0
##                        
##                for l in landList:
##                    l.change_grid(-1)
##                    gameGrid = l.update_grid(gameGrid)
##
##                player.changePos(-GRIDSIZE)

                print player.gridRect

        elif event.type == KEYUP:

            if event.key == K_LEFT:
                if player.state == LEFTRUN:
                    player.changeState(IDLE)

            if event.key == K_RIGHT:
                if player.state == RIGHTRUN:
                    player.changeState(IDLE)

        elif event.type == CHANGETILEEVENT:
            
            for x in xrange(GRIDX+2):
                for y in xrange(GRIDY+1):
                    gameGrid[(x,y)] = 0

            for l in landList:
                l.change_grid(event.x,event.y)
                gameGrid = l.update_grid(gameGrid)

            player.changePos(event.x*GRIDSIZE,event.y*GRIDSIZE)

            try:
                pruneGrid(gameGrid,-5,15)
            except:
                print "Prune error. Replace this with the gamelose event." #TODO

            fillColor = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        

    gameSurf.fill(LIGHTBLUE)

    #gameSurf = draw_grid(gameSurf,GRIDSIZE)

    #gameSurf = demo_sprites(list1,gameSurf,GRIDSIZE)
    #gameSurf.blit(list3[tileIndex[random.choice(TILEINDEX.keys())]],(0,0))
    #gameSurf.blit(list1[1],(0,0))
    #gameSurf.blit(sheet1,(0,0),(16, 80, 16, 16))

    #gameSurf = land1.blit_surf(gameSurf)

    for x in landList:
        gameSurf = x.blit_surf(gameSurf)
    #gameSurf = land2.blit_surf(gameSurf)

    for a in aniList:
        PLAYEROFFSETX += a.update(timePassed)
        gameSurf = a.draw(gameSurf)

    timeSinceGridShift += timePassedSeconds

    if (SCREENX,SCREENY) != (GAMEX,GAMEY):
        offset = -GRIDSIZE*(timeSinceGridShift/gridSpeed)*(SCREENX/float(GAMEX))
        newSurf = pygame.transform.scale(gameSurf,(SCREENX,SCREENY))
        DISPLAYSURF.blit(newSurf,(offset,0))
        DISPLAYSURF.fill(fillColor,(SCREENX-GRIDSIZE*(SCREENX/float(GAMEX)),0,GRIDSIZE*(SCREENX/float(GAMEX)),SCREENY))
                         
    else:
        DISPLAYSURF.blit(gameSurf,(0,0))
        
    pygame.display.update()

    if timeSinceGridShift >= gridSpeed:
        pygame.event.post(pygame.event.Event(CHANGETILEEVENT,x=-1,y=0))
        timeSinceGridShift = 0


    timePassed = clock.tick(FPS)
    timePassedSeconds = timePassed/1000.
#"""
