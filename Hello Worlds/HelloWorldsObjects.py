#########               Griffin Tang ~ Class Objects File              #########
#####                             Hello Worlds                             #####
################################################################################
#                    Small Functions Adapted From Koz Below                    #
################################################################################
#####                               Imports:                               #####
import math,random,pygame,decimal,os,sys
from pygame.locals import *
import pygame.gfxdraw

def roundHalfUp(d): #112 Function
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))
#####                                                                      #####
################################################################################
#############################    CLASS CREATION    #############################
################################################################################

class SpaceObject(object):

    def __init__(self,x,y):
        self.expansionFactor = 1
        self.xPos = x
        self.yPos = y
        self.xVel = 0
        self.yVel = 0
        self.G = 6.67*(10**(-11))
        self.startVelConstant = .25

    def expand(self,maxRadius):
        if self.radius < maxRadius:
            self.radius += self.expansionFactor

    def getCoords(self):
        return (self.xPos,self.yPos)
        
    def getDistance(self,other):
        x0,y0 = self.getCoords()
        x1,y1 = other.getCoords()
        distance = ( (x1-x0)**2 + (y1-y0)**2 )**0.5
        return distance

    def mouseUpdate(self, x, y):
        self.xPos = x
        self.yPos = y

    def getClosestSun(self, suns):
        if len(suns) == 0: pass
        closest = None
        smallestDistance = 1000
        for sun in suns:
            if self.getDistance(sun) < smallestDistance:
                closest = sun
                smallestDistance = self.getDistance(sun)
        return closest

    def startVelocity(self,x,y):
        xStart = int(abs(self.xPos - x) * self.startVelConstant) #absurd without
        yStart = int(abs(self.yPos - y) * self.startVelConstant) #proportion control
        
        if x > self.xPos: #Broken up by pos and neg coords
            xStart = -xStart
            if y > self.yPos:
                yStart = -yStart #Trajectory is opposite of mouse position
        else:
            if y > self.yPos:
                yStart = -yStart
        self.xVel += xStart
        self.yVel += yStart

    def gravUpdate(self, suns):
        if isinstance(self,Sun): return
        if len(suns) != 0: 
            sun = self.getClosestSun(suns)
            if sun == None: return
            sunX,sunY = sun.xPos, sun.yPos
            dist = self.getDistance(sun)
            if dist == 0: return
            force = (self.G * (self.mass * sun.mass)) / dist**2 #graity equation
            #need to split force into x/y using similar triangles to find angle
            xDist = abs(self.xPos - sun.xPos)
            theta = math.acos(xDist/dist) #adjacent / hypotenuse
            #Split force with the angle
            #First Quadrant
            if self.xPos > sun.xPos and self.yPos < sun.yPos:
                xForce = (math.cos(theta) * force)
                yForce = (math.sin(theta) * force)

                self.xVel -= roundHalfUp(xForce)
                self.yVel += roundHalfUp(yForce)
            #Second Quadrant
            elif self.xPos < sun.xPos and self.yPos < sun.yPos:
                xForce = (math.cos(theta) * force)
                yForce = (math.sin(theta) * force)    

                self.xVel += roundHalfUp(xForce)
                self.yVel += roundHalfUp(yForce)            

            #Third Quadrant
            elif self.xPos < sun.xPos and self.yPos > sun.yPos:
                xForce = (math.cos(theta) * force)
                yForce = (math.sin(theta) * force)    

                self.xVel += roundHalfUp(xForce)
                self.yVel -= roundHalfUp(yForce)  
            #Fourth Quadrant
            elif self.xPos > sun.xPos and self.yPos > sun.yPos:
                xForce = (math.cos(theta) * force)
                yForce = (math.sin(theta) * force)    

                self.xVel -= roundHalfUp(xForce)
                self.yVel -= roundHalfUp(yForce)  

    def collisionCheck(self,suns):
        if len(suns)!=0: 
            sun = self.getClosestSun(suns)
            if sun == None: return
            sX,sY,sR = sun.xPos,sun.yPos,sun.radius
            #Check all possibilities for both radii
            for x in range(self.xPos-self.radius,self.xPos+self.radius):
                for y in range(self.yPos-self.radius,self.yPos+self.radius):
                    if (sX-sR < x < sX+sR) and (sY-sR < y < sY+sR): return True
        return False

    def velocityUpdate(self):
        self.xPos += self.xVel
        self.yPos += self.yVel 

    def drawObj(self, screen):
        pygame.draw.circle(screen, self.color,(self.xPos,self.yPos),self.radius)

class Sun(SpaceObject): ######################### SUN ##########################
    suns = []
    def __init__(self,x,y,radius=None):
        self.startRadius = 10
        if radius == None:
            self.radius = self.startRadius #starting default radius for SUN
        else: self.radius = radius
        super().__init__(x,y) 
        self.maxRadius = 70
        self.mass = self.radius * (10**(9))
        self.color = self.updateColor() #Sun has color proportional to size
        self.suns.append(self)

    def expand(self):
        super().expand(self.maxRadius)
        self.color = self.updateColor() #must also update sun's color

    def drawObj(self, screen):
        pygame.draw.circle(screen, self.color,(self.xPos,self.yPos),self.radius)

    def updateColor(self):
        r,g,b = 250,250,0 #Start with Yellow
        k = self.radius/(self.maxRadius + self.startRadius)#Get proportion
         #Make the sun redder as it gets larger
        g = int(225 - 225*k)
        return (r,g,b)

class Player(SpaceObject): ###################### PLANET #######################
    players = []
    def __init__(self,x,y):
        #Rotating the orignal rocket every time allows the rocket
        #to not become distorted badly over time
        self.originalRocket = self.initRocket()
        self.rocket = self.originalRocket
        self.rect = self.rocket.get_rect()
        (blue, green, purple, cyan, pink) = ((0,0,255),(0,255,0),
                                          (150,0,150),(0,150,150),(255,150,150))

        self.colors = [blue,green,purple,cyan,pink]
        self.color = self.getColor() #(0,0,255)#self.getColor()
        self.radius = 10 #Starting default radius for PLANET
        self.maxRadius = 40
        self.mass = 1 * (10**(5))
        super().__init__(x,y)
        self.players.append(self)

    def initRocket(self): #tilt the rocket to the right
        rocket = pygame.image.load('images/rocket.bmp')
        angle = -90
        rocket = pygame.transform.rotate(rocket, angle)
        return rocket

    def getColor(self):
        return self.colors[random.randint(0,len(self.colors)-1)]

    def expand(self):
        super().expand(self.maxRadius)

    def drawObj(self, screen):
        xBump, yBump= self.rocket.get_width()//2,self.rocket.get_height()//2
        screen.blit(self.rocket,(self.xPos-xBump,self.yPos-yBump))

    def rotatePlayer(self):
        #FUNCTION HEAVILY ADAPTED, BUT INSPIRED BY PYGAME WIKI 
        #http://pygame.org/wiki/RotateCenter?parent=
        angle,rect = self.getPlayerAngle(),self.originalRocket.get_rect()
        rocket = pygame.transform.rotate(self.originalRocket, angle)
        rect = rocket.get_rect(center=rect.center)
        self.rocket = rocket
        #self.rect = rect

    def getPlayerAngle(self): #Get the angle based on velocity

        radians = 0 #default

        #First Quad
        if self.xVel > 0 and self.yVel > 0:
            radians = -math.atan(self.yVel/self.xVel)
        #Second Quad
        elif self.xVel < 0 and self.yVel > 0:
            radians = math.pi - math.atan(self.yVel/self.xVel) 
        #Third Quad
        elif self.xVel < 0 and self.yVel < 0:
            radians = math.pi - math.atan(self.yVel/self.xVel)
        #Fourth Quad
        elif self.xVel > 0 and self.yVel < 0:
            radians = -math.atan(self.yVel/self.xVel)

        angle = radians * 180/math.pi #Convert to degrees
        return angle
    
class Button(object):
    def __init__(self,x,y,text,associatedValue):
        lvlSize = 30
        textSize = 70
        (blue, green, purple, cyan, pink,darkRed,slate,sea) = (
        (0,0,255),(0,255,0),(150,0,150),(0,150,150),(255,150,150),(139,0,0),
        (72,61,139),(46,139,87))
        self.colors = [blue,green,purple,cyan,pink,darkRed,slate,sea]
        self.color = self.getColor()
        self.txts = text.split('.')
        self.x = x
        self.y = y
        if isinstance(associatedValue,int): self.r = lvlSize #Level button size
        else: self.r = textSize #radius
        self.link = associatedValue

    def getColor(self):
        return self.colors[random.randint(0,len(self.colors)-1)]

    def __eq__(self,other):
        return self.link == other.link

    def __hash__(self):
        return hash(self.link)

    def drawButton(self,screen):
        white = (255,255,255)
        pygame.draw.circle(screen,self.color,(self.x,self.y),self.r)
        path = os.path.abspath('Fonts/BlackHoleBB.ttf')
        font = pygame.font.Font(path,34)
        for i in range(len(self.txts)):
            text = font.render(self.txts[i], 1, white)
            xBump = text.get_width()//2
            yBump = text.get_height()//2
            screen.blit(text,(self.x-xBump,self.y-yBump*(len(self.txts)-i)))
        #text = font.render(self.txt[0], 1, white)
        #xBump = text.get_width()//2
        #yBump = text.get_height()//2
        #screen.blit(text,(self.x-xBump,self.y-yBump))

    def isClicked(self,x,y):
        return ((self.x - self.r < x < self.x + self.r) and 
            (self.y - self.r < y < self.y + self.r))

    #Endzones
class End(object):
    def __init__(self,x,y,xlen,ylen):
        self.x = x
        self.y = y
        self.xlen = xlen
        self.ylen = ylen

    def drawEnd(self,screen):
        red = (255,0,0)
        pygame.draw.rect(screen,red,(self.x,self.y,self.xlen,self.ylen), 2)

#Background Stars
class BgStar(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        (white,grey,yellow,lightblue,pink) = ((255,255,255),(155,155,155),
                                        (255,255,0),(155,155,255),(255,155,155))
        self.colors = [white,grey,white,yellow,white,lightblue,pink]
        self.color = self.getColor()
        self.rMin,self.rMax = 2,5 #Radius min/max
        self.r = self.getRadius()
        self.twinkle = False #Is flashed?
        self.bgColor = (0, 0, 25)

    def getColor(self):
        i = random.randint(0,len(self.colors)-1)
        return self.colors[i]

    def getRadius(self):
        return random.randint(self.rMin,self.rMax)

    def drawBGStar(self,screen):    
        #Draw Central star
        pygame.draw.circle(screen,self.color,(self.x,self.y),self.r)
        #If twinkled, draw the twinkling
        if not self.twinkle:
            #Top Right
            pygame.draw.circle(screen,self.bgColor,(self.x+self.r,self.y-self.r),self.r)
            #Top Left
            pygame.draw.circle(screen,self.bgColor,(self.x-self.r,self.y-self.r),self.r)
            #Bot Right
            pygame.draw.circle(screen,self.bgColor,(self.x+self.r,self.y+self.r),self.r)
            #Bot Left
            pygame.draw.circle(screen,self.bgColor,(self.x-self.r,self.y+self.r),self.r)

class VectorBubble(SpaceObject):
    def __init__(self,x,y,suns):
        self.xPos = x
        self.yPos = y
        self.force = self.getForce(suns)
        self.fMax = 30
        try: self.fRatio = self.force/self.fMax
        except: self.fRatio = 0
        self.color = self.getColor()
        self.maxRadius = 8
        self.r = self.getRadius()
        self.suns = suns
        
    def getColor(self):
        #Start neon green, work to deep brown
        r = 255 * self.fRatio
        g = 255 - 255 * self.fRatio
        b = 0
        return (r,g,b)

    def getRadius(self):
        return int(self.maxRadius * self.fRatio)

    def drawBubble(self,screen):
        pygame.gfxdraw.filled_circle(screen,self.xPos,self.yPos,self.r,self.color)

    def getForce(self, suns):
        if len(suns) != 0: 
            sun = self.getClosestSun(suns)
            if sun == None: return
            sunX,sunY = sun.xPos, sun.yPos
            dist = self.getDistance(sun)
            if dist == 0: return
            force = (sun.G * sun.mass) / dist**2 #graity equation
            force *= 10**5
            if force > 30: force = 30
            return int(force)

class Explosion(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.render = pygame.image.load('images/explosion.bmp')

    def drawExplosion(self,screen):
        xBump, yBump = self.render.get_width()//2, self.render.get_height()//2
        screen.blit(self.render,(self.x - xBump,self.y - yBump))

class CustomDataObj(object):
    def __init__(self,tag):
        self.tag = tag #Incase i need more than one
        self.suns = []
        self.players = []
        self.ends = []
        self.endStart = None,None #Coords of new endzone
        self.endFin = None,None
        self.fakeEndFin = None,None
        self.pressed = False #Spacebar pressed to create sun
        self.sunX,self.sunY = None,None
        self.drawingEnd = False #Create shadow box for creating ends
        self.undoing = False #to undo suns
        self.saving = False #to save level
        self.bubbleFrequency = 15 #How often a bubble is laid
        self.help = False #Help for level customizer screen

class SoundLibrary(object): #container for sound effects
    def __init__(self,tag):
        self.tag = tag
        self.goal = pygame.mixer.Sound("Sounds/goal.wav")
        self.crash = pygame.mixer.Sound("Sounds/blast.wav")
        self.launch = pygame.mixer.Sound("Sounds/launch.wav")
        self.outOfBounds = pygame.mixer.Sound("Sounds/reset.wav")

class ImageLibrary(object):
    def __init__(self,tag):
        self.tag = tag
        self.player = pygame.image.load('Images/rocket.bmp')
        self.explosion = pygame.image.load('Images/explosion.bmp')

    def drawFakePlayer(self,x,y,screen,rotated=False):
        xBump, yBump = self.player.get_width()//2, self.player.get_height()//2
        if not rotated:
            screen.blit(self.player,(x - xBump, y - yBump))
        else:
            rocket = pygame.image.load('Images/rocket.bmp')
            angle = -135
            rocket = pygame.transform.rotate(rocket, angle)
            screen.blit(rocket,(x - xBump, y - yBump))

