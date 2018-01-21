################################################################################
#########                   Griffin Tang Term Project                  #########
#####                             Hello Worlds                             #####
################################################################################
# Pygame framework adapted from Lukas Peraz; Small Functions Adapted From Koz  #
#       Music From SEGA's Space Harrier, Goal sound from Nintendo's Mario      #
#Fallback music from http://www.playonloop.com/2016-music-loops/galactic-chase/#
#         Death, Out of Bounds, and Launch sounds from soundBible.com          #
#        Explosion image from https://pixabay.com/p-417894/?no_redirect        #
# Rocket image from https://openclipart.org/detail/28806/a-cartoon-moon-rocket #
#   Learned how to do music from https://www.youtube.com/watch?v=YQ1mixa9RAw   #
#                      Fonts all from www.fontspace.com
################################################################################
#####                               Imports:                               #####
import math,random,pygame,decimal,os,sys,threading
import os
#from pygame.locals import *
from HelloWorldsObjects import *
#import pygame.font

def roundHalfUp(d): #112 Function
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))
#####                                                                      #####
################################################################################
# TO EXIT WINDOW: SHIFT + W
################################################################################
###########################    Pygame Structure    #############################
################################################################################

class HelloWorlds(object):
    custom = CustomDataObj('customScreen') #Create a data struct for custom lvls
    suns = []
    players = []
    ends = []
    bgStars = [] #Background Stars
    twinkledStars = []
    explosions = []
    homeScreenObjs = []
    menuButtons = []
    levelButtons = []
    pausedButtonData = [[],[],[]]
    vectorBubbles = []
    mouseOneHold = False
    mouseTwoHold = False
    spawnHold = False

    def init(self, screen = 'homeScreen'):
        pygame.init()
        self.screen = screen
        self.buttonHeight, self.buttonWidth = 100, 300
        self.bump = self.buttonHeight/6
        self.start, self.clicked = True, False #Start Sequence, Start Game
        self.levelPath = os.path.abspath("levels.txt")
        self.level, self.tries = 0, 0
        self.strtX,self.strtY,self.strtR = self.width//2, self.height//2, 50
        self.buttonDif = 200 #distance from buttons to center object
        self.maxBounds = 200 #Max distance offscreen
        self.paused, self.passed = False, False
        self.lastScreen = 'homeScreen'
        self.totalLines = self.getTextDocData()
        self.numberOfStars,self.twinkleChance = 300, 500 #number of stars, prob
        self.getBGStars()
        self.playerStartXY = (None,None)
        self.powerLineCoords = (None,None,None,None)
        self.scores = ["Incomplete"] * self.totalLines
        self.jamItUp(); self.initImages(); self.initFonts()
    
    def callWithLargeStack(f,*args):
        threading.stack_size(2**27)  # 64MB stack
        sys.setrecursionlimit(2**27) # will hit 64MB stack limit first
        # need new thread to get the redefined stack size
        def wrappedFn(resultWrapper): resultWrapper[0] = f(*args)
        resultWrapper = [None]
        #thread = threading.Thread(target=f, args=args)
        thread = threading.Thread(target=wrappedFn, args=[resultWrapper])
        thread.start()
        thread.join()
        return resultWrapper[0]
 

    def jamItUp(self):
        self.gameSounds = SoundLibrary('gameSounds') #Init sound effects object
        mixerValues = [44100,16,2,4096] #Arbitrary values for my frequency etc.
        pygame.mixer.pre_init(mixerValues[0],mixerValues[1],mixerValues[2])
        pygame.mixer.init()
        try: pygame.mixer.music.load("sounds/background.wav")
        except: pygame.mixer.music.load("sounds/secondBackground.wav")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1) #play continuously

    def initImages(self):
        self.gameImages = ImageLibrary('gameImages')

    def initFonts(self):
        path = os.path.abspath('Fonts/SFOuterLimitsUpright.ttf')
        path2 = os.path.abspath('Fonts/BlackHoleBB.ttf')
        path3 = os.path.abspath('Fonts/Digital_tech.otf')
        self.titleFont = pygame.font.Font(path,130)
        self.subtitleFont = pygame.font.Font(path,70)
        self.buttonFont = pygame.font.Font(path2,30)
        self.fontSmall = pygame.font.Font(path3,20)
        self.font = pygame.font.Font(path3,35)
        self.fontMed = pygame.font.Font(path3,43)
        self.fontBig = pygame.font.Font(path3,50)
        self.fontHuge = pygame.font.Font(path3,70)
        

    def getTextDocData(self):
        levelDoc = open(self.levelPath,'r')
        levelText = levelDoc.read().splitlines()
        return len(levelText)
        
    def planetaryMovement(self,players,suns):
        for player in players:
            if player.collisionCheck(suns):
                pygame.mixer.Sound.play(self.gameSounds.crash)
                self.explosions.append(Explosion(player.xPos,player.yPos))
                self.players.pop(self.players.index(player))
            elif self.screen == 'homeScreen' or self.clicked: 
                player.gravUpdate(suns)
                player.velocityUpdate()

    def getBGStars(self):
        stars = []
        stars.append(self.bgRecursion(stars))
        stars = stars[:-1] #Get rid of the original list call
        self.bgStars = stars
        
    def bgRecursion(self, stars):
        if len(stars) == self.numberOfStars:return stars
        else:
            #Setup for isLegal
            x = random.randint(0,self.width)
            y = random.randint(0,self.height)
            newStar = BgStar(x,y)
            #isLegal
            if stars == []: stars.append(newStar)
                    #if distance between last star and new star < max radius
            elif not ((abs(stars[-1].x - x) < 2*stars[-1].rMax) or 
                      (abs(stars[-1].y - y) < 2*stars[-1].rMax)):
                stars.append(newStar)

            self.bgRecursion(stars)

    def twinkleStars(self):
        returnChance = 5
        for star in self.bgStars:
            if random.randint(0,self.twinkleChance)==self.twinkleChance:
                star.twinkle == True
                self.twinkledStars.append(star)
                self.bgStars.pop(self.bgStars.index(star))
        for twinkled in self.twinkledStars:
            if random.randint(0,returnChance)==returnChance:
                twinkled.twinkle == False
                self.bgStars.append(twinkled)
                self.twinkledStars.pop(self.twinkledStars.index(twinkled))

    #LEFT CLICK
    def mouseOnePressed(self, x, y):
        if self.screen == 'homeScreen': self.homeScreenMouseOnePressed(x,y)
        elif self.screen == 'menuScreen': self.menuScreenMouseOnePressed(x,y)
        elif self.screen == 'playScreen': self.playScreenMouseOnePressed(x,y)
        elif self.screen == 'helpScreen': self.helpScreenMouseOnePressed(x,y)
        elif self.screen == 'levelScreen': self.levelScreenMouseOnePressed(x,y)
        elif self.screen =='customScreen': self.customScreenMouseOnePressed(x,y)
        elif self.screen == 'scoreScreen': self.scoreScreenMouseOnePressed(x,y)
        
    def mouseOneReleased(self, x, y):
        if self.screen =='customScreen': self.customScreenMouseOneReleased(x,y)

    def mouseMotion(self, x, y):
        if self.screen == 'playScreen':self.playScreenMouseMotion(x,y)
        elif self.screen == 'customScreen': self.customScreenMouseMotion(x,y)

    def mouseOneDrag(self, x, y):
        pass

    #RIGHT CLICK
    def mouseTwoPressed(self, x, y):
        if self.screen =='customScreen': self.customScreenMouseTwoPressed(x,y)

    def mouseTwoReleased(self, x, y):
        if self.screen =='customScreen':self.customScreenMouseTwoReleased(x,y)

    def mouseTwoDrag(self, x, y):
        pass

    #KEYBOARD
    def keyPressed(self, keyCode, modifier):
        pass

    def keyReleased(self, keyCode, modifier):
        pass

    def timerFired(self, dt): ################################## TIMER FIRED
        self.twinkleStars()
        if self.isKeyPressed(ord('f')): #A fun easter egg
            self.numberOfStars, self.twinkleChance = 900, 1
            self.getBGStars()
        #else: self.numberOfStars,self.twinkleChance = 300, 500
        if self.screen == 'homeScreen': self.homeScreenTimerFired(dt)
        elif self.screen == 'menuScreen': self.menuScreenTimerFired(dt)
        elif self.screen == 'playScreen': self.playScreenTimerFired(dt)
        elif self.screen == 'levelScreen': self.levelScreenTimerFired(dt)
        elif self.screen == 'customScreen': self.customScreenTimerFired(dt)
        elif self.screen == 'scoreScreen': self.scoreScreenTimerFired(dt)

    def redrawAll(self, screen):
        self.drawBackground(screen)
        if self.screen == 'homeScreen': self.homeScreenRedrawAll(screen)
        elif self.screen == 'menuScreen': self.menuScreenRedrawAll(screen)
        elif self.screen == 'playScreen': self.playScreenRedrawAll(screen)
        elif self.screen == 'helpScreen': self.helpScreenRedrawAll(screen)
        elif self.screen == 'levelScreen': self.levelScreenRedrawAll(screen)
        elif self.screen =='customScreen':self.customScreenRedrawAll(screen)
        elif self.screen == 'scoreScreen': self.scoreScreenRedrawAll(screen)

    def drawBackground(self,screen):
        for star in self.bgStars:
            star.drawBGStar(screen)

    def draw(self,screen):
        for planet in HelloWorlds.planets:
            planet.drawObj(screen)
        for sun in HelloWorlds.suns:
            sun.drawObj(screen)

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=1280, height=800, fps=40, title="Hello Worlds"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = "Hello Worlds"
        self.bgColor = (0, 0, 25)
        pygame.init()

################################## HOME ########################################
    def homeScreenMouseOnePressed(self,x,y):
        #Play Button
        white, posX, posY = (255,0,0), self.width//2, 3*self.height//4
        text = self.subtitleFont.render("Play", 1, white)
        xBump, yBump = text.get_width()//2,text.get_height()//2
        xFactor, yFactor = 4*xBump, 3*yBump
        xBound,yBound,xlen,ylen = posX-2*xBump,posY+yBump//2,xFactor,yFactor

        if xBound < x < xBound+xlen and yBound<y<yBound+ylen:
            self.start = True
            self.screen = "menuScreen"

    def homeScreenTimerFired(self,dt):
        if self.start == True: #Hardcode a perfect orbit around a sun
            self.homeScreenObjs = []
            self.players = []
            sunRad = 50
            self.homeScreenObjs.append(Sun(self.width//2,self.height//2,sunRad))
            demoPlanet = Player(self.width//2,self.height//6)
            demoPlanet.xVel = 36
            demoPlanet.yVel = 4
            demoPlanet.radius = 20
            self.players.append(demoPlanet)
            self.start = False

        else:
            if len(self.players) == 0: #planet missing
                self.start = True
            else:
                self.players[-1].rotatePlayer()
                self.planetaryMovement([self.players[-1]],
                                                       [self.homeScreenObjs[0]])
        
    def homeScreenRedrawAll(self, screen):
        for obj in self.homeScreenObjs:
            obj.drawObj(screen)
        for player in self.players:
            player.drawObj(screen)
        self.drawTitleText(screen)
        self.drawPlayButton(screen)
        self.drawHomeScreenToolTip(screen)

    def drawTitleText(self, screen):
        white = (255,255,255)
        headerText = self.titleFont.render("Hello Worlds!", 1, white)
        xBump,yBump = headerText.get_width()//2, headerText.get_height()//2
        xPos,yPos = self.width//2, yBump//2
        screen.blit(headerText,(xPos-xBump,yPos))
        msg = '~lOst in SpAce~'
        subTitle = self.subtitleFont.render(msg, 1, white)
        xPos, yPos = self.width//2, self.height//5
        xBump = subTitle.get_width()//2
        screen.blit(subTitle,(xPos-xBump,yPos))

    def drawPlayButton(self,screen):
        white = (255,255,255)
        red = (255,0,0)
        posX, posY = self.width//2, 3*self.height//4
        text = self.subtitleFont.render("plAy", 1, white)
        xBump, yBump = text.get_width()//2, text.get_height()//2
        helper = (7/6)
        screen.blit(text,(posX-xBump, posY+yBump*helper))
        xFactor, yFactor = 4*xBump, 3*yBump
        pygame.draw.rect(screen, white,
                                (posX-2*xBump,posY+yBump//2,xFactor,yFactor), 2)

    def drawHomeScreenToolTip(self,screen):
        white = (255,255,255)
        xPos, yPos = self.width//2, 17*self.height//18
        msg = 'press shift and q to exit'
        text = self.font.render(msg, 1, white)
        xBump, yBump = text.get_width()//2, text.get_height()//2
        screen.blit(text,(xPos-xBump, yPos-yBump))


################################## MENU ########################################

    def menuScreenMouseOnePressed(self,x,y):
            #Start Button
        if ((self.strtX-self.strtR < x < self.strtX+self.strtR) and 
            (self.strtY-self.strtR < y < self.strtY+self.strtR)):
            self.start = True
            self.level = 0
            self.paused = False
            self.tries = 0
            self.screen = 'playScreen'
        else:
            for button in self.menuButtons:
                if button.isClicked(x,y):
                    self.start = True
                    self.totalLines = self.getTextDocData()
                    self.screen = button.link

    def menuScreenTimerFired(self,dt):
        if self.start == True:
            self.lastScreen = 'menuScreen'
            if self.menuButtons == []:
                self.menuButtons.append(Button(self.strtX,
                        self.strtY-self.buttonDif,"Level.Select",'levelScreen'))
                self.menuButtons.append(Button(self.strtX,
                                 self.strtY+self.buttonDif,"Back",'homeScreen'))
                self.menuButtons.append(Button(self.strtX-self.buttonDif,
                                                self.strtY,"Help",'helpScreen'))
                self.menuButtons.append(Button(self.strtX+self.buttonDif,
                                     self.strtY,"Level.Creator",'customScreen'))
                self.menuButtons.append(Button(self.strtX,
                                             self.strtY,"Scores",'scoreScreen'))
                for i in range(len(self.menuButtons)):
                    x,y = self.menuButtonPosCalc(i)
                    self.menuButtons[i].x = x
                    self.menuButtons[i].y = y
            self.start = False

    def menuScreenRedrawAll(self, screen):
        self.drawStartButton(screen)
        self.drawMenuButtons(screen)

    def menuButtonPosCalc(self,buttonNumber):
        buttonDist = (self.width//80)*len(self.menuButtons)
        if buttonDist < 250:
            buttonDist = 250
        #Ratio of button number in a circle
        theta = (buttonNumber/len(self.menuButtons))*(2*math.pi)
        bump = math.pi/2
        x,y = math.cos(theta-bump)*buttonDist,math.sin(theta-bump)*buttonDist
        x += self.width//2
        y += self.height//2
        return int(x),int(y)

    def drawStartButton(self, screen):
        orange = (255,100,0)
        white = (255,255,255)
        pygame.draw.circle(screen,orange,(self.strtX,self.strtY),self.strtR)
        text = self.buttonFont.render("Begin", 1, white)
        xBump = text.get_width()//2
        yBump = text.get_height()//2
        screen.blit(text,(self.strtX-xBump, self.strtY-yBump))

    def drawMenuButtons(self,screen):
        for button in self.menuButtons:
            button.drawButton(screen)

################################## HELP ########################################
    def helpScreenMouseOnePressed(self,x,y):
        black = (0,0,0)
        text = self.fontMed.render("Back", 1, black)
        xpos,ypos = (self.width//2 - text.get_width(), 
                                        5*self.height//6 + text.get_height()//2)
        xlen,ylen = 2*text.get_width(),text.get_height()
        if ((xpos - xlen < x < xpos + xlen) and (ypos- ylen < y < ypos + ylen)):
            self.start = True
            self.screen = self.lastScreen

    def helpScreenRedrawAll(self,screen):
        self.drawHelpScreenBox(screen)
        self.drawHelpBack(screen)
        self.drawHelpText(screen)

    def drawHelpScreenBox(self,screen):
        white = (255,255,255)
        #font = pygame.font.SysFont("georgia", 100)
        text = self.fontHuge.render("How to Play", 1, white)
        xBump = text.get_width()/2
        screen.blit(text,(self.width//2-xBump, self.height//6))
        boxData =[self.width//8,self.height//8,6*self.width//8,2*self.height//3]
        pygame.draw.rect(screen, white, 
                               (boxData[0],boxData[1],boxData[2],boxData[3]), 2)

    def drawHelpBack(self,screen):
        white = (255,255,255)
        text = self.fontMed.render("Back", 1, white)
        xBump = text.get_width()//2
        yBump = text.get_height()//2
        xpos,ypos = self.width//2 - text.get_width(), 5*self.height//6-yBump
        xlen,ylen = 2*text.get_width(),2*text.get_height()
        screen.blit(text,(self.width//2-xBump, 5*self.height//6))
        pygame.draw.rect(screen, white, (xpos,ypos,xlen,ylen), 2)

    def drawHelpText(self,screen):
        white = (255,255,255)
        msg = 'Sling yourself around the suns by clicking'
        text = self.fontMed.render(msg, 1, white)
        xBump = text.get_width()//2
        yBump = text.get_height()//2
        screen.blit(text,(self.width//2-xBump, self.height//3))
        msg = 'opposite to the direction you want to go.'
        text = self.fontMed.render(msg, 1, white)
        xBump = text.get_width()//2
        screen.blit(text,(self.width//2-xBump, self.height//3+2*yBump))
        msg = 'To win, gravitate yourself into the portal!'
        text = self.fontMed.render(msg, 1, white)
        xBump = text.get_width()//2
        screen.blit(text,(self.width//2-xBump, self.height//3+13*yBump))
        xlen,ylen,red, orange, blue = 100,50,(255,0,0),(255,150,0),(123,123,255)
        xpos,ypos,r1,r2 = self.width//2 + xlen//2,self.height//3 + 7*yBump,40,15
        pygame.draw.rect(screen, red,(xpos,ypos,xlen,ylen), 2)
        pygame.draw.circle(screen,orange,(xpos-xlen,ypos+ylen),r1)
        self.gameImages.drawFakePlayer(xpos,ypos,screen,True)

############################### LEVEL SELECT ###################################
    def levelScreenMouseOnePressed(self,x,y):
        #Start Button
        if ((self.strtX-self.strtR < x < self.strtX+self.strtR) and 
            (self.strtY-self.strtR < y < self.strtY+self.strtR)):
                self.start = True
                self.paused = False
                self.tries = 0
                self.screen = 'playScreen'
        for button in self.levelButtons:
            if button.isClicked(x,y):
                self.level = button.link   
        #Button to Level Creater Handler
        white = (255,255,255)
        msg = "Create Level"
        text = self.font.render(msg, 1, white)
        xBump = text.get_width()//2
        customScreenBox = [3*self.width//4-xBump//2,6*self.height//8,150+xBump,60]
        if ((customScreenBox[0] < x < customScreenBox[0] +customScreenBox[2])and
            (customScreenBox[1] < y < customScreenBox[1] + customScreenBox[3])):
            self.screen = 'customScreen'
        #Back Button Handler
        backBox = boxData = [self.width//8 - 23,6*self.height//8,150,60]
        if ((backBox[0] < x < backBox[0] + backBox[2]) and
            (backBox[1] < y < backBox[1] + backBox[3])):
            self.screen = 'menuScreen'

    def levelScreenTimerFired(self,dt):
        #Buttons take x,y,text,associatedValue
        if self.start or len(self.levelButtons) < self.totalLines:
            for i in range(self.totalLines):
                x,y = self.levelButtonPosCalc(i)
                msg = str(i+1) #level # should start at 1, not 0
                #Link level # to button
                #Make sure we arent doubke maing buttons
                if Button(x,y,msg,i) not in self.levelButtons:
                    self.levelButtons.append(Button(x,y,msg,i))
            self.start = False
            for i in range(len(self.levelButtons)):
                x,y = self.levelButtonPosCalc(i)
                self.levelButtons[i].x = x
                self.levelButtons[i].y = y

    #Calculate where the button should go in a circle
    def levelButtonPosCalc(self,buttonNumber):
        buttonDist = (self.width//80)*self.totalLines
        if buttonDist < 100:
            buttonDist = 100
        #Ratio of button number in a circle
        theta = (buttonNumber/self.totalLines)*(2*math.pi)
        x,y = math.cos(theta)*buttonDist,math.sin(theta)*buttonDist
        x += self.width//2
        y += self.height//2
        return int(x),int(y)

    def levelScreenRedrawAll(self,screen):
        self.drawLevelEnterButton(screen)
        self.drawButtons(screen)
        self.drawCreateLevelButton(screen)
        self.drawLevelBackButton(screen)

    def drawLevelEnterButton(self, screen):
        orange = (255,100,0)
        white = (255,255,255)
        pygame.draw.circle(screen,orange,(self.strtX,self.strtY),self.strtR)
        msg = "Enter %s" %(self.level + 1)
        text = self.fontSmall.render(msg, 1, white)
        xBump = text.get_width()//2
        yBump = text.get_height()//2
        screen.blit(text,(self.strtX-xBump, self.strtY-yBump))

    def drawButtons(self, screen):
        for button in self.levelButtons:
            button.drawButton(screen)

    def drawCreateLevelButton(self,screen):
        boxData = [3*self.width//4,6*self.height//8,150,60]
        
        white = (255,255,255)
        msg = "Create Level"
        text = self.font.render(msg, 1, white)
        xBump,yBump = text.get_width()//2,text.get_height()//2
                        #Explanation: startpos + 1/2(length) - 1/2(wordlen)
        screen.blit(text,((boxData[0]+boxData[2]//2)-xBump,
                                              (boxData[1]+boxData[3]//2-yBump)))
        pygame.draw.rect(screen, white, 
                (boxData[0]-xBump//2,boxData[1],boxData[2]+xBump,boxData[3]), 2)
    
    def drawLevelBackButton(self,screen):
        white = (255,255,255)
        msg = "Back"
        text = self.font.render(msg, 1, white)
        xBump,yBump = text.get_width()//2,text.get_height()//2
        boxData = [self.width//8 - 23,6*self.height//8,150,60]
        pygame.draw.rect(screen, white, 
                               (boxData[0],boxData[1],boxData[2],boxData[3]), 2)
                        #Explained: startpos + 1/2(length) - 1/2(wordlen)
        screen.blit(text,
            ((boxData[0]+boxData[2]//2)-xBump,(boxData[1]+boxData[3]//2-yBump)))


############################# LEVEL CUSTOMIZER #################################    
    
    def customScreenMouseMotion(self,x,y):
        self.custom.sunX,self.custom.sunY = x,y
        #if suns not empty, let the sun be moved about
        if self.custom.suns != [] and self.custom.pressed:
            self.custom.suns[-1].xPos,self.custom.suns[-1].yPos = x,y
        #If we're drawing, give it something to draw
        self.custom.fakeEndFin = x,y
        
    def getEndCoords(self):
        x0,y0 = self.custom.endStart
        wX,wY = self.custom.endFin #working x and y
        xlen,ylen = abs(x0 - wX), abs(y0 - wY)
        if wX < x0: xlen = -xlen
        if wY < y0: ylen = -ylen
        return x0,y0,xlen,ylen
            
    #Left Click
    def customScreenMouseOnePressed(self,x,y):
        if self.custom.players != []: self.custom.players.pop()
        self.custom.players.append(Player(x,y))

    def customScreenMouseOneReleased(self,x,y):
        pass

    #Right Click
    def customScreenMouseTwoPressed(self,x,y):
        self.custom.drawingEnd = True
        self.custom.endStart = (x,y)

    def customScreenMouseTwoReleased(self,x,y):
        #Clear the ends list if it's not empty
        #x0,y0,xlen,ylen = self.width//2,self.height//2,30,30
        self.custom.endFin = (x,y)
        x0,y0,xlen,ylen = self.getEndCoords()
        if self.custom.ends != []:
            self.custom.ends.pop()
        self.custom.drawingEnd = False
        self.custom.ends.append(End(x0,y0,xlen,ylen))

    #Timer Fired
    def customScreenTimerFired(self,dt):
        #Left click to create player
        #Right click and drag to create end
        #Create suns and expand with space
        if self.isKeyPressed(ord(' ')):
            if not self.custom.pressed: 
                self.custom.suns.append(Sun(self.custom.sunX,self.custom.sunY))
            self.custom.pressed = True
            self.custom.suns[-1].expand()
        else: self.custom.pressed = False
        #Undo suns with 'z'
        if self.isKeyPressed(ord('z')) and self.custom.suns != []: 
            if not self.custom.undoing: self.custom.suns.pop()
            self.custom.undoing = True
        else: self.custom.undoing = False
        #Save level with enter
        if (self.isKeyPressed(ord('s')) and (self.custom.suns != []) and 
           (self.custom.players != []) and (self.custom.ends != [])): 
            if not self.custom.saving: 
                self.encodeLevel(); self.screen = 'homeScreen'
            self.custom.saving = True
        else: self.custom.saving = False
        if self.isKeyPressed(ord('h')):
            self.custom.help = True
        else: self.custom.help = False
        if self.isKeyPressed(27):
            self.resetLevelCustomizer()
            self.screen = "menuScreen"

    def resetLevelCustomizer(self):
        self.custom.suns = []
        self.custom.players = []
        self.custom.ends = []

    def encodeLevel(self):
        doc = open(self.levelPath,'a')
        #player
        entry = "%s.%s:"%(self.custom.players[-1].xPos,
                                                   self.custom.players[-1].yPos)
        #end
        x,y,xlen,ylen = self.calcEndPoints()
        entry += "%s.%s.%s.%s:"%(x,y,xlen,ylen)
        for sun in self.custom.suns:
            x,y,radius = sun.xPos,sun.yPos,sun.radius
            entry += '%s.%s.%s:'%(x,y,radius)
        doc.write('\n'+entry)
        doc.close()
        self.custom.suns = []
        self.custom.players = []
        self.custom.ends = []
        self.scores += ['Incomplete']
        msg, i = str(self.totalLines+1), self.totalLines
        x,y = self.levelButtonPosCalc(i)
        self.levelButtons.append(Button(x,y,msg,i))
        self.start = True
        
    def calcEndPoints(self):
        x,y = self.custom.ends[-1].x,self.custom.ends[-1].y
        x0,y0 = x,y
        xlen,ylen = self.custom.ends[-1].xlen,self.custom.ends[-1].ylen
        if xlen < 0: #if the square was made backwards
            x0 = x+xlen
        if ylen < 0:
            y0 = y+ylen
        xL,yL = abs(xlen),abs(ylen)
        return x0,y0,xL,yL

    #Draw Functions
    def customScreenRedrawAll(self,screen):
        for player in self.custom.players:
            player.drawObj(screen)
        for sun in self.custom.suns:
            sun.drawObj(screen)
        for end in self.custom.ends:
            end.drawEnd(screen)
        if self.custom.drawingEnd:
            self.drawFakeEnd(screen)
        if self.custom.help:
            self.drawHelpBox(screen)
        self.drawToolTip(screen)

    def drawFakeEnd(self,screen):
        gray = (125,125,150)
        x0,y0 = self.custom.endStart
        x1,y1 = self.custom.fakeEndFin
        xlen,ylen = abs(x0 - x1), abs(y0 - y1)
        if x1 < x0: xlen = -xlen
        if y1 < y0: ylen = -ylen
        pygame.draw.rect(screen,gray,(x0,y0,xlen,ylen),1)

    def drawToolTip(self,screen):
        white = (255,255,255)
        font = pygame.font.SysFont("georgia", 30)
        stringPart2 = '''Press Esc to exit or S to save and exit!'''
        msg = '''Hold  H  for help %s '''%stringPart2
        text = self.font.render(msg, 1, white)
        xBump,yBump = text.get_width()//8,text.get_height()//2
        screen.blit(text,(xBump,yBump))

    def drawHelpBox(self,screen):
        self.drawCustomizerHelpBox(screen)
        self.drawCustomizerText(screen)
        self.drawCustomizerHelpObjs(screen)

    def drawCustomizerHelpBox(self,screen):
        white = (255,255,255)
        gray = (0,0,25)
        msg = '-Controls-'
        text = self.fontBig.render(msg, 1, white)
        xBump,yBump = text.get_width()//2,text.get_height()//2
        
        x,y,xlen,ylen = (self.width//4,self.height//4,self.width//2,
                                                                 self.height//2)
        pygame.draw.rect(screen, gray, (x,y,xlen,ylen))
        pygame.draw.rect(screen, white, (x,y,xlen,ylen),3)
        screen.blit(text,(self.width//2-xBump,self.height//4 + yBump))
        y += yBump*4
        pygame.draw.line(screen, white,(x,y),(x+xlen,y),3)

    def drawCustomizerText(self,screen):
        white = (255,255,255)
        msg = 'Left Click to add a player'
        text = self.font.render(msg, 1, white)
        xBump,yBump = text.get_width()//2,text.get_height()//2
        screen.blit(text,(self.width//4+yBump,self.height//3+2*yBump))
        msg = 'Hover and Hold Space to add a Sun'
        text = self.font.render(msg, 1, white)
        screen.blit(text,(self.width//4+yBump,self.height//3+4*yBump))
        msg =  'Right Click and Drag to add a Portal'
        text = self.font.render(msg, 1, white)
        screen.blit(text,(self.width//4+yBump,self.height//3+6*yBump))
        msg =  'Press Z to undo Suns or Press S to save/exit'
        text = self.fontSmall.render(msg, 1, white)
        xBump = text.get_width()//2
        screen.blit(text,(self.width//2-xBump,self.height//3+10*yBump))

    def drawCustomizerHelpObjs(self,screen):
        red = (255,0,0)
        pColor = (155,0,155)
        orange = (255,155,0)
        x, y, r, xlen, ylen = 3*self.width//4,3*self.height//4, 20,-50,-50
        bump = 20
        pygame.draw.rect(screen, red, (x-2*bump,y-2*bump,xlen,ylen), 3)
        x -= self.width//2
        bump *= 3
        self.gameImages.drawFakePlayer(x+bump,y-bump,screen)
        x = self.width//2
        r *= 2
        pygame.draw.circle(screen, orange, (x,y-bump), r)

################################## PLAY ########################################
    def playScreenMouseOnePressed(self,x,y):
        if self.paused:
            #perams formatted as x,y,xlen,ylen
            #perams in the order NextLevel, Menu, Help
            for i in range(len(self.pausedButtonData)):
                perams = self.pausedButtonData[i]
                if perams == []: continue
                if ((perams[0] < x < perams[0] + perams[2]) and
                    (perams[1] < y < perams[1] + perams[-1])):
                    if i == 0 and self.passed:
                        if self.players != []: #clear if needed
                            self.players.pop()
                        self.tryNextLevel()
                    elif i == 1:
                        self.screen = 'menuScreen'
                    elif i == 2:
                        self.lastScreen = 'playScreen'
                        self.screen = 'helpScreen'
        elif not self.clicked:
            pygame.mixer.Sound.play(self.gameSounds.launch)
            self.tries += 1
            if self.players != []: #Fixes the smallest bug on the planet
                self.players[-1].startVelocity(x,y)
            self.clicked = True

    def tryNextLevel(self):
        self.totalLines = self.getTextDocData()
        if self.level+1 == self.totalLines:
            self.screen = 'scoreScreen'
        else:
            self.vectorBubbles = [] #Clear vector Bubbles
            self.level += 1
            self.tries = 0
            self.paused, self.passed,self.clicked = False, False, False
            self.start = True

    def playScreenMouseMotion(self,x,y):
        self.calcPowerLine(x,y)

    def playScreenTimerFired(self,dt):
        if self.players != []:
            self.players[-1].rotatePlayer()
        if self.isKeyPressed(ord('r')):
            self.players[-1].rotatePlayer()
        if self.isKeyPressed(ord('h')):
            self.createVectorField()
        if self.start == True:
            self.initPlayObjects()
            self.start = False
        else:
            self.planetaryMovement(self.players,self.suns)
            if len(self.players) == 0 or self.boundsCheck():
                if not self.passed and len(self.players) != 0:
                    pygame.mixer.Sound.play(self.gameSounds.outOfBounds)
                self.resetGame()
            elif self.isGoal():
                pygame.mixer.Sound.play(self.gameSounds.goal)
                self.scores[self.level] = self.tries
                self.passed = True
                self.paused = True

    def initPlayObjects(self):
        #Text doc formatted as:
            #player(x,y):endZone(x,y,xlen,ylen):sun(x,y,size)...
            #Create Objects from the text doc
            self.explosions = []
            self.getTextDocData()
            levelDoc = open(self.levelPath,'r')
            levelText = levelDoc.read().splitlines()[self.level]
            playerData = levelText.split(':')[0].split('.')
            self.players = []
            players = [Player(int(playerData[0]),int(playerData[1]))]
            self.players = players
            endData = levelText.split(':')[1].split('.')
            ends = [End(int(endData[0]),int(endData[1]),
                                               int(endData[2]),int(endData[3]))]
            self.ends = ends
            sunDataUnits = levelText.split(':')[2:] #Arbitrary number of suns
            if sunDataUnits[-1] == '': sunDataUnits.pop()
            suns = []
            for sunDataSlot in sunDataUnits:
                sunData = sunDataSlot.split('.')
                suns.append(Sun(int(sunData[0]),int(sunData[1]),
                                                               int(sunData[2])))
            self.suns = suns
            self.playerStartXY = self.players[-1].xPos, self.players[-1].yPos
                
    def playScreenRedrawAll(self, screen):
        self.drawLevelObjs(screen)
        self.drawPlayToolTips(screen)
        self.drawTries(screen)
        if (not self.clicked and (None not in self.powerLineCoords) 
                                                           and not self.paused): 
            self.drawPowerLine(screen)
        if self.paused:
            self.drawPaused(screen)

    def resetGame(self):
        self.start = True
        self.clicked = False
        if len(self.players) != 0: self.players.pop()

    def isGoal(self):
        #Player x and y
        x,y = self.players[-1].xPos, self.players[-1].yPos
        #Goal x, y, length, and width
        gX,gY = self.ends[-1].x, self.ends[-1].y
        gXLen,gYLen = self.ends[-1].xlen, self.ends[-1].ylen
        return ((gX < x < gX + gXLen) and (gY < y < gY + gYLen))

    def boundsCheck(self):
        x,y = self.players[-1].xPos, self.players[-1].yPos
        return ((-self.maxBounds > x) or (x > self.width + self.maxBounds) or 
            (-self.maxBounds > y) or (y > self.height + self.maxBounds))
    
    def calcPowerLine(self,x,y):
        x0,y0 = self.playerStartXY
        dist = ( (x-x0)**2 + (y-y0)**2 )**0.5
        xDist = abs(x - x0)
        if dist == 0: dist = 1
        theta = math.acos(xDist/dist) #adjacent / hypotenuse
        x1,y1 = x0, y0 
        #First Quadrant
        if x > x0 and y < y0:
            x1 -= (math.cos(theta) * dist)
            y1 += (math.sin(theta) * dist)
        #Second Quadrant
        elif x < x0 and y < y0:
            x1 += (math.cos(theta) * dist)
            y1 += (math.sin(theta) * dist)
        #Third Quadrant
        elif x < x0 and y > y0:
            x1 += (math.cos(-theta) * dist)
            y1 += (math.sin(-theta) * dist)
        #Fourth Quadrant
        elif x > x0 and y > y0: 
            x1 -= (math.cos(theta) * dist)
            y1 -= (math.sin(theta) * dist)

        self.powerLineCoords = (x0,y0,x1,y1)

    def drawPowerLine(self,screen):
        gray = (155,155,155)
        red = (50,50,75)
        x0,y0,x1,y1 = self.powerLineCoords
        pygame.draw.line(screen, red, [x0,y0],[x1,y1],3)

    def createVectorField(self):
        #VectorBubble objects take x,y,suns
        self.vectorBubbles = []
        for x in range(0,self.width,self.custom.bubbleFrequency):
            for y in range(0,self.height,self.custom.bubbleFrequency):
                self.vectorBubbles.append(VectorBubble(x,y,self.suns))

    def drawLevelObjs(self,screen):
        if self.isKeyPressed(ord('h')) and self.suns != []: #Make sure it has
            for bubble in self.vectorBubbles:               #things to draw
                bubble.drawBubble(screen)
        for player in self.players:
            player.drawObj(screen)
        for sun in self.suns:
            sun.drawObj(screen)
        for end in self.ends:
            end.drawEnd(screen)
        for explosion in self.explosions:
            explosion.drawExplosion(screen)

    def drawTries(self,screen):
        white = (255,255,255)
        insertText = "Tries: %s" %self.tries
        text = self.fontBig.render(insertText, 1, white)
        xBump, yBump = text.get_width()//2,text.get_height()
        screen.blit(text,(self.width - text.get_width()*2,
                                                       text.get_height()-yBump))

    def drawPlayToolTips(self,screen):
        helpPoint = 3
        white = (255,255,255)
        msgOverhang = '''to slow down and display vector fields!'''
        msg = '''Press 'P' to pause and 'H' %s'''%msgOverhang
        text = self.fontSmall.render(msg, 1, white)
        xBump = text.get_width()//2
        yBump = text.get_height()//2
        if self.tries <= helpPoint:
            screen.blit(text,(xBump//2, yBump))

    def drawPaused(self,screen):
        yDif = 50 #Offset between buttons
        white = (255,255,255)
        if self.passed: 
            msg = "Level Complete!"
            #Next level
            font = pygame.font.SysFont("georgia", 50)
            nextText = 'Next Level'
            if self.level == self.totalLines-1:
                msg = 'Last Level Complete'
                nextText = 'View Scores'
            text = self.fontBig.render(nextText, 1, white)
            xBump = text.get_width()//2
            x,y,xlen,ylen=(self.width//2-xBump,
                         self.height//2-yDif,text.get_width(),text.get_height())
            screen.blit(text,(x,y))
            self.pausedButtonData[0] = [int(x),y,xlen,ylen]

        else: msg = "Level Paused"
        text = self.fontBig.render(msg, 1, white)
        xBump = text.get_width()/2
        x,y,xlen,ylen=(self.width//2-xBump,self.height//4+yDif,text.get_width(),
                                                              text.get_height())
        screen.blit(text,(x,y))
        pygame.draw.rect(screen, white, (self.width//4,self.height//4,
                                               self.width//2,self.height//2), 3)
        
        #Menu
        text = self.fontBig.render('Menu', 1, white)
        xBump = text.get_width()/2
        x,y,xlen,ylen=(self.width//2-xBump,self.height//2,text.get_width(),
                                                              text.get_height())
        screen.blit(text,(x,y))
        self.pausedButtonData[1] = [int(x),y,xlen,ylen]

        #Help
        text = self.fontBig.render('Help', 1, white)
        xBump = text.get_width()/2
        x,y,xlen,ylen=(self.width//2-xBump,self.height//2+yDif,text.get_width(),
                                                              text.get_height())
        screen.blit(text,(x,y))
        self.pausedButtonData[2] = [int(x),y,xlen,ylen]

################################### SCORE ######################################
    def scoreScreenMouseOnePressed(self,x,y):
        #data for hitbox sizing
        white = (255,255,255)
        text = self.fontBig.render('Reset Course', 1,white)
        xBump,yBump = text.get_width()/2,text.get_height()//2
        x0,y0,xlen,ylen=((3*self.width//4-xBump)-yBump,(self.height//2)-yBump,
                             text.get_width()+2*yBump,text.get_height()+2*yBump)
        #Reset the scores
        if ((x0 < x < x0 + xlen) and (y0 < y < y0 + ylen)):
            self.scores = ['Incomplete'] * self.totalLines
        else:
            self.screen = 'homeScreen'

    def scoreScreenTimerFired(self,dt):
        pass

    def scoreScreenRedrawAll(self,screen):
        self.drawScoreHelp(screen)
        self.drawScores(screen)
        self.drawStats(screen)
        self.drawScoreScreenButtons(screen)

    def drawScoreHelp(self,screen):
        white = (255,255,255)
        mixed = (155,155,180)
        #SCORES:
        msg = "Your Scores:"
        text = self.fontHuge.render(msg, 1, white)
        xBump = text.get_width()//2
        yBump = text.get_height()//2
        x,y=self.width//2-xBump, self.height//8-yBump
        screen.blit(text,(x,y))
        #"Click anywhere"
        msg = "click anywhere to return to the home screen"
        text = self.font.render(msg, 1, mixed)
        xBump = text.get_width()//2
        yBump = int(2*yBump//3)
        x,y = self.width//2-xBump, self.height//4-2*yBump #old msg's y values
        screen.blit(text,(x,y))
        lineY = self.height//4
        pygame.draw.line(screen,white,(0,lineY),(self.width,lineY),5)

    def drawScores(self,screen):
        white = (255,255,255)
        scoreStartHeight = self.height//4 - 30
        #if we start at 1/4 and end on the 3rd quarter we have 1/2 to work with
        textBuffer =  (self.height - 2*scoreStartHeight) // self.totalLines
        minBuffer = 40
        if textBuffer < minBuffer: textBuffer = minBuffer
        
        scoreMessages = []
        for i in range(len(self.scores)):
            txt = self.fontSmall.render('Level %s Tries %s'%((i+1),self.scores[i]), 1, 
                                                                          white)
            screen.blit(txt,(self.width//4,scoreStartHeight + textBuffer*(i+1)))

    def drawScoreScreenButtons(self,screen):
        col = None
        white = (255,255,255)
        gray = (155,155,180)
        if self.scores == ['Incomplete'] * self.totalLines:
            col = gray 
        else: col = white
        
        text = self.fontBig.render('Reset Course', 1, col)
        xBump,yBump = text.get_width()/2,text.get_height()//2
        x,y,xlen,ylen=(3*self.width//4-xBump,self.height//2,text.get_width(),
                                                              text.get_height())
        screen.blit(text,(x,y))
        pygame.draw.rect(screen,col,
                                  (x-yBump,y-yBump,xlen+2*yBump,ylen+2*yBump),2)

    def drawStats(self,screen):
        white = (255,255,255)
        courseAverage = 0
        playedCourses = 0
        courseTotal = 0
        if self.scores != ['Incomplete'] * self.totalLines:
            for score in self.scores:
                if score != "Incomplete":
                    playedCourses += 1
                    courseTotal += score
            courseAverage = courseTotal // playedCourses
        #Average
        text = self.fontBig.render('Average Tries: ' + str(courseAverage),
                                                                       1, white)
        xBump,yBump = text.get_width()//2, 2*text.get_height()//2
        x,y=3*self.width//4-xBump,self.height//3-yBump
        screen.blit(text,(x,y))

        #Coures Played
        text = self.font.render('Levels Played: ' + str(playedCourses),
                                                                       1, white)
        xBump = text.get_width()//2#, text.get_height()//2
        x,y=3*self.width//4-xBump,self.height//3
        screen.blit(text,(x,y))

        #Total Score
        text = self.font.render('Course Total: ' + str(courseTotal), 1, white)
        xBump= text.get_width()//2#, text.get_height()//2
        x,y=3*self.width//4-xBump,self.height//3+yBump
        screen.blit(text,(x,y))

################################################################################

    def run(self):

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height),
                                               pygame.NOFRAME)
        # set the title of the window
        pygame.display.set_caption(self.title)

        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        self.init()
        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                #LEFT CLICK
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mouseOnePressed(*(event.pos))

                elif event.type == pygame.MOUSEMOTION:
                    self.mouseMotion(*(event.pos)) 

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseOneReleased(*(event.pos))

                elif (event.type == pygame.MOUSEMOTION and 
                                                    event.buttons[2] == 1):
                    self.mouseTwoDrag(*(event.pos))

                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseOneDrag(*(event.pos))

                #RIGHT CLICK
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.mouseTwoPressed(*(event.pos))

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    self.mouseTwoReleased(*(event.pos))                

                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    if event.key == ord("q") and event.mod == 1: #Shift + W
                        playing = False
                    elif event.key == ord('p'):
                        self.paused = not(self.paused)
                    self.keyPressed(event.key, event.mod)

                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)

                elif event.type == pygame.QUIT:
                    playing = False

            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()

def main():
    game = HelloWorlds()
    game.run()

if __name__ == '__main__':
    main()

"""
162.373:1114.127.95.532:476.371.33:894.381.32:
256.227:1146.141.87.476:951.173.35:807.83.33:633.166.32:803.496.67:
187.160:1065.650.214.149:413.294.29:668.426.34:960.579.43:
443.143:894.490.129.114:587.456.26:793.246.26:870.469.35:1047.618.13:1050.619.34:
696.764:427.99.521.162:979.338.32:693.339.34:403.334.34:546.553.38:858.552.35:
160.300:900.100.50.500:460.150.40:760.350.40
160.300:900.100.50.500:400.400.30:800.400.30
89.247:898.252.29.167:356.314.27:719.309.23:
644.100:117.551.204.72:395.281.28:542.562.29:
88.229:831.172.162.412:666.355.34:502.577.30:
"""