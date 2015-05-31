#Cut+Run
#Project for Mini LD 59: Swap
#May 2015
#by Joe Cowman

import pygame
from pygame.locals import *
from sys import exit
import random
import math

FPS = 60

SCREENX, SCREENY = (1080,720)
GAMEX,GAMEY = (320,208)
GRIDX,GRIDY = (19,12) #For coordinates, so there are actually 1 more of each tile
GRIDSIZE = 16

GRAVCONSTANT = 20 #tiles/s^2
GRIDSPEED = 0.5 #sec/shift

SHIFTAMOUNT = 20

INCLUDEFILE = "IncludedSpritesheets.txt"
FONT = "8bitoperator.ttf"

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY1 = (125,125,125)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
LIGHTBLUE = (100,255,255)
COLORKEY = (1,1,1)

BGCOLOR = LIGHTBLUE

IDLE = "Idle"
LEFTRUN = "LeftRun"
LEFTFACE = "LeftFace"
RIGHTRUN = "RightRun"
RIGHTFACE = "RightFace"

UP = "Up"
RIGHT = 1
DOWN = "Down"
LEFT = -1

GAME = 0
TITLE = 1

STARTSCREEN = 0

pygame.init()

DISPLAYSURF = pygame.display.set_mode((SCREENX,SCREENY))

pygame.display.set_caption("Cut+Run")

global gameSurf
gameSurf = pygame.Surface((GAMEX,GAMEY))

gameGrid = {}

for x in xrange(GRIDX+1):
    for y in xrange(GRIDY+1):
        gameGrid[(x,y)] = 0

global PLAYEROFFSETX
PLAYEROFFSETX = 0

CHANGETILEEVENT = USEREVENT + 1
PLAYERLOSEEVENT = USEREVENT + 2

TILEINDEX = {"a":32,"b":33,"c":34,"d":35,"e":36,"f":37,"g":38,"h":39,"i":40,"j":41,"k":42,"l":43,"m":44,"n":45,"o":46,"p":47,"q":48,"r":49,"s":50,"t":51,"u":52,"v":53,"w":54,"x":55,"y":56,"z":57,"1":58,"2":59,"3":60,"4":61,"5":62,"6":63}
TERRAINLISTS = [["b","a","c","d","e","f","g","h"],["j","i","k","l","m","n","o","p"],["q","r","s","t"],["u","v","w","x"],["y","z"],["1","2","3","4","5"],["6"]]

#sprite ranges for each animated character
P1o,P1 = (0,9)
P2o,P2 = (9,18)
P3o,P3 = (18,27)

BGSQUARE = pygame.Surface((GRIDSIZE,GRIDSIZE))
BGSQUARE.fill(BGCOLOR)

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
            if t not in ["0","!"]:
                self.typeDict[t] = self.spriteList[TILEINDEX[t]]
                self.rectDict[t] = self.typeDict[t].get_bounding_rect()

        self.typeDict["!"] = BGSQUARE

        self.surf = self.render_surf()

        self.gridCoords = gridCoords
        self.gridX,self.gridY = gridCoords

    def change_grid(self,x=0,y=0):
        self.gridX += x
        self.gridY += y
        self.gridCoords = (self.gridX,self.gridY)

    def set_grid(self,x=None,y=None):
        if x is not None:
            self.gridX = x
        if y is not None:
            self.gridY = y
        self.gridCoords = (self.gridX,self.gridY)

    def update_grid(self,globalGrid,step=GRIDSIZE):

        for row in xrange(len(self.terrain)):
            
            for column in xrange(len(self.terrain[row])):

                terrainIndex = self.terrain[row][column]
                
                if terrainIndex != "0":

                    if terrainIndex == "!":
                        
                        globalGrid[(self.gridX+column,self.gridY+row)] = 0

                    else:
                    
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

    def jump(self,override=False,boost=0):
        
        if self.onSolidGround or override:
            self.vy = -(self.jumpPower+boost)
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

        if self.state == LEFTFACE:
            if self.vx < 0:
                self.vx += self.moveSpeed*(msPassed/1000.0)
                self.vx = min(0,self.vx)
            elif self.vx > 0:
                self.vx -= self.moveSpeed*(msPassed/1000.0)
                self.vx = max(0,self.vx)

            if not self.vx:
                self.changeState(IDLE)

        if self.state == RIGHTFACE:
            if self.vx < 0:
                self.vx += self.moveSpeed*(msPassed/1000.0)
                self.vx = min(0,self.vx)
            elif self.vx > 0:
                self.vx -= self.moveSpeed*(msPassed/1000.0)
                self.vx = max(0,self.vx)

            if not self.vx:
                self.changeState(IDLE)

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

                if self.state == LEFTFACE or self.state == RIGHTFACE:
                    self.changeState(IDLE)


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

    def checkFall(self,mercybuffer=20):

        return self.y > GAMEY + mercybuffer

    def checkSpriteCollide(self,targetSprite):

        targetBound = targetSprite.boundBox

        return self.boundBox.colliderect(targetBound)

    def getHit(self,DIRECTION,changeState=True):

        #direction should be direction of collision
        
        self.vx = random.randint(1,4)*random.randint(1,self.moveSpeed)
        self.jump(True)

        if DIRECTION == RIGHT:
            self.vx = -self.vx
            
            if changeState:
                self.changeState(LEFTFACE)

        elif DIRECTION == LEFT:
            if changeState:
                self.changeState(RIGHTFACE)

    def draw(self,destSurf):

        destSurf.blit(self.spriteList[self.spriteIndex],self.coords)
        
        return destSurf

class Enemy(Anisprite):

    def __init__(self,direction,jumpyness,spriteSlice,initGridCoords,moveSpeed=0,jumpPower=0,allowFloat=False,aniSpeed=80,step=GRIDSIZE):
        
        super(Enemy,self).__init__(spriteSlice,initGridCoords,moveSpeed,jumpPower,allowFloat,aniSpeed,step)

        if direction == LEFT:
            self.changeState(LEFTRUN)

        elif direction == RIGHT:
            self.changeState(RIGHTRUN)

        self.jumpyness = jumpyness
        self.timeSinceJumpCheck = 0
        self.direction = direction #enemy only attribute

    def update(self,msPassed,step=GRIDSIZE,screenDim=(GAMEX,GAMEY),gridDim=(GRIDX,GRIDY),globalGrid=gameGrid):

        msPassed2 = min(msPassed,1000./FPS)
        self.timeSinceJumpCheck += msPassed2/1000.

        if self.timeSinceJumpCheck >= 1:
            self.timeSinceJumpCheck = 0

            if random.randint(0,100) < self.jumpyness:
                self.jump()

        return super(Enemy,self).update(msPassed,step,screenDim,gridDim,globalGrid)

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
        
        x = 5 #default
        deltaX = 0

        deltaX = random.randint(-1,1)*random.randint(0,noiseFactor+int((random.random()**2)*random.randint(0,noiseFactor**2)))

        x += deltaX

        x = max(x,1)

        if x > 8:
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
        terrainList[-1].set_grid(0)
        xStep += dimList[t][0]

    return terrainList

def genEnemy(spriteLists):

    listChoice = random.choice(spriteLists)
    indexChoice = random.randint(1,3)

    if indexChoice == 1:
        index1 = P1o
        index2 = P1
        
    elif indexChoice == 2:
        index1 = P2o
        index2 = P2

    elif indexChoice == 3:
        index1 = P3o
        index2 = P3

    direction = random.choice([LEFT,RIGHT])

    jumpyness = int(100-random.randint(0,100)*random.random()*0.5)

    if direction == RIGHT:
        x = random.randint(-1,4)

    elif direction == LEFT:
        x = random.randint(GRIDX-3,GRIDX+1)
    
    y = random.randint(-5,-1)

    speed = int((random.randint(30,130) + random.randint(0,130) + random.randint(0,130))/3.)

    jump = int((random.randint(50,250) + random.randint(50,250))/2.)

    enemy = Enemy(direction,jumpyness,listChoice[index1:index2],(x,y),speed,jump)

    return enemy

spriteLists = []

spriteSheetFilenames = [line.strip() for line in open(INCLUDEFILE)][1:] #don't include header

for f in spriteSheetFilenames:
    spriteLists.append(get_sprites(get_spritesheet(f),GRIDSIZE))

doGame = True

currentScreen = STARTSCREEN

levelUpFont = pygame.font.Font(FONT,32)

while True:

    onTitle = True
    
    playerList = 0
    playerIndex1 = P1o
    playerIndex2 = P1

    pCoords = (720,100)
    pScale = (200,200)

    pSurf = spriteLists[playerList][playerIndex1]
    tranSurf = pygame.transform.scale(pSurf,pScale)

    cutRunFont = pygame.font.Font(FONT,100)
    cutRunSurf = cutRunFont.render("Cut+Run",True,WHITE)
    cutRunCoords = (100,100)

    subFont = pygame.font.Font(FONT,32)
                                    
    sub1Surf = subFont.render("code by Joe Cowman",True,WHITE)
    sub1Coords = (108,218)

    sub2Surf = subFont.render("graphics by 77 others",True,WHITE)
    sub2Coords = (108,250)

    insFont = pygame.font.Font(FONT,40)

    ins1Surf = insFont.render("LEFT/RIGHT: Select Character",True,WHITE)
    ins1Coords = (0.5*(SCREENX-ins1Surf.get_width()),400)

    ins2Surf = insFont.render("SPACE: Start Game",True,WHITE)
    ins2Coords = (0.5*(SCREENX-ins2Surf.get_width()),470)

    ins3Surf = insFont.render("ESCAPE: Quit",True,WHITE)
    ins3Coords = (0.5*(SCREENX-ins3Surf.get_width()),540)

    while onTitle:

        for event in pygame.event.get():

            if event.type == QUIT:
                exit()

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    exit()

                if event.key == K_SPACE:
                    onTitle = False

                if event.key == K_RIGHT:

                    if playerIndex1 == P1o:
                        playerIndex1 = P2o
                        playerIndex2 = P2

                    elif playerIndex1 == P2o:
                        playerIndex1 = P3o
                        playerIndex2 = P3

                    elif playerIndex1 == P3o:
                        playerIndex1 = P1o
                        playerIndex2 = P1
                        playerList += 1

                    if playerList >= len(spriteLists):
                        playerList = 0

                if event.key == K_LEFT:

                    if playerIndex1 == P1o:
                        playerIndex1 = P3o
                        playerIndex2 = P3
                        playerList -= 1

                    elif playerIndex1 == P2o:
                        playerIndex1 = P1o
                        playerIndex2 = P1

                    elif playerIndex1 == P3o:
                        playerIndex1 = P2o
                        playerIndex2 = P2

                    if playerList < 0:
                        playerList = len(spriteLists) - 1

                pSurf = spriteLists[playerList][playerIndex1]
                tranSurf = pygame.transform.scale(pSurf,pScale)

        DISPLAYSURF.fill(BLACK)

        DISPLAYSURF.blit(tranSurf,pCoords)
        DISPLAYSURF.blit(cutRunSurf,cutRunCoords)
        DISPLAYSURF.blit(sub1Surf,sub1Coords)
        DISPLAYSURF.blit(sub2Surf,sub2Coords)
        DISPLAYSURF.blit(ins1Surf,ins1Coords)
        DISPLAYSURF.blit(ins2Surf,ins2Coords)
        DISPLAYSURF.blit(ins3Surf,ins3Coords)

        pygame.display.update()

    #print "Starting Game..."
    doGame = True

    landList = []
    queuedLandList = []

    queuedLandList += genGround(20,1,spriteLists,3,0)

    for l in landList:
        gameGrid = l.update_grid(gameGrid)

    player = Anisprite(spriteLists[playerList][playerIndex1:playerIndex2],(3,3),90,206,False)

    aniList = [player]

    noiseLevel = 1
    maxEnemies = 0

    gridSpeed = GRIDSPEED
    timeSinceGridShift = 0.

    fillColor = (0,0,0)

    totalXTile = 0
    tilesSinceShift = 0

    landXTile = 0
    maxTilesOnScreen = GRIDX+1

    toDelete = []

    levelUpSurf = levelUpFont.render("Wave 1",True,BLACK)
    levelUpCoords = (0.5*(SCREENX-levelUpSurf.get_width()),20)
    timeSinceLevelUp = 0.

    clock = pygame.time.Clock()
    timePassed = clock.tick()
    timePassedSeconds = timePassed/1000.

    while doGame:

        toDelete = []

        while landXTile < maxTilesOnScreen:

            try:
                land = queuedLandList.pop(0)
            except:
                land = genGround(20,1,spriteLists,3,0)[0]
                
            land.change_grid(landXTile)
            landXTile += land.numX
            landList.append(land)

        if len(aniList) - 1 < maxEnemies:
            aniList.append(genEnemy(spriteLists))

        if tilesSinceShift >= SHIFTAMOUNT:
            
            tilesSinceShift = 0
            
            noiseLevel += 1
            gridSpeed *= .95

            if random.randint(0,maxEnemies*2) < len(aniList):
                maxEnemies += 1

            levelUpString = "Wave %i: Speed + 5%%, %i Enemies" % (noiseLevel, maxEnemies)

            queuedLandList += genGround(20,noiseLevel,spriteLists,3,0)

            levelUpSurf = levelUpFont.render(levelUpString,True,BLACK)
            levelUpCoords = (0.5*(SCREENX-levelUpSurf.get_width()),20)

            #print "level up!",noiseLevel,gridSpeed,maxEnemies

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
                    pass

                if event.key == K_ESCAPE:
                    exit()

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

                for a in aniList:
                    a.changePos(event.x*GRIDSIZE,event.y*GRIDSIZE)

                try:
                    pruneGrid(gameGrid,-5,15)
                    
                except:
                    pass


                delList = []

                for n in xrange(len(landList)):
                    land = landList[n]
                    if land.gridX < -land.numX - 5:
                        delList.append(n)

                for d in delList:
                    del landList[d]
                    for i in xrange(len(delList)):
                        delList[i] -= 1 #indexes will change

                fillColor = (random.randint(0,255),random.randint(0,255),random.randint(0,255))

                landXTile -= 1
                totalXTile += 1
                tilesSinceShift += 1

            elif event.type == PLAYERLOSEEVENT:
                #print "You Lose!"
                doGame = False
            

        gameSurf.fill(BGCOLOR)

        for x in landList:
            gameSurf = x.blit_surf(gameSurf)
            
        currentPlayer = aniList[0]

        PLAYEROFFSETX += currentPlayer.update(timePassed)
        gameSurf = currentPlayer.draw(gameSurf)

        if currentPlayer.checkFall():
            pygame.event.post(pygame.event.Event(PLAYERLOSEEVENT))

        if len(aniList) > 1:

            for a in aniList[1:]:
                a.update(timePassed)
                gameSurf = a.draw(gameSurf)
                
                if a.checkFall():
                    toDelete.append(a)

                if a.checkSpriteCollide(currentPlayer):
                    currentPlayer.getHit(a.direction)


        for t in toDelete:
            aniList.pop(aniList.index(t))
                    

        timeSinceGridShift += timePassedSeconds

        if (SCREENX,SCREENY) != (GAMEX,GAMEY):
            offset = -GRIDSIZE*(timeSinceGridShift/gridSpeed)*(SCREENX/float(GAMEX))
            newSurf = pygame.transform.scale(gameSurf,(SCREENX,SCREENY))
            DISPLAYSURF.blit(newSurf,(offset,0))
            DISPLAYSURF.fill(fillColor,(SCREENX-GRIDSIZE*(SCREENX/float(GAMEX)),0,GRIDSIZE*(SCREENX/float(GAMEX)),SCREENY))
                             
        else:
            DISPLAYSURF.blit(gameSurf,(0,0))

        if levelUpSurf:
            DISPLAYSURF.blit(levelUpSurf,levelUpCoords)

            timeSinceLevelUp += timePassedSeconds

            if timeSinceLevelUp >= 4:
                timeSinceLevelUp = 0
                levelUpSurf = None
            
        pygame.display.update()

        if timeSinceGridShift >= gridSpeed:
            
            pygame.event.post(pygame.event.Event(CHANGETILEEVENT,x=-1,y=0))
            timeSinceGridShift = 0


        timePassed = clock.tick(FPS)
        timePassedSeconds = timePassed/1000.

    spacePressed = False
    
    scoreFont = pygame.font.Font(FONT,64)
    scoreSurf = scoreFont.render("Your Score: %i" % totalXTile,True,WHITE)
    scoreCoords = (0.5*(SCREENX-scoreSurf.get_width()),0.5*(SCREENY-1.5*scoreSurf.get_height()))

    againFont = pygame.font.Font(FONT,30)
    againSurf = againFont.render("Press SPACE to play again or ESCAPE to quit.",True,WHITE)
    againCoords = (0.5*(SCREENX-againSurf.get_width()),scoreCoords[1]+scoreSurf.get_height())

    while not spacePressed:

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

            if event.type == KEYDOWN:
                
                if event.key == K_SPACE:
                    spacePressed = True

                elif event.key == K_ESCAPE:
                    exit()

        DISPLAYSURF.fill(BLACK)

        DISPLAYSURF.blit(scoreSurf,scoreCoords)
        DISPLAYSURF.blit(againSurf,againCoords)

        pygame.display.update()

