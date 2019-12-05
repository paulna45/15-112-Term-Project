# Contains all information about the objects 
# (the Player, the Enemy types, and the Food)

from tkinter import *
from PIL import Image, ImageTk
import random, math, decimal


# from https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html#HelperFunctions
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

# from https://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html#customColors
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

class Agar(object):
    def __init__(self, mode, cx, cy):
        self.mode = mode
        self.cx = cx
        self.cy = cy
        self.dx = 0
        self.dy = 0
        self.r = random.randint(0,255)
        self.g = random.randint(0,255)
        self.b = random.randint(0,255)
        self.color = rgbString(self.r, self.g, self.b)
        self.radiusQueue = 0
    
    def __hash__(self):
        return hash(self.getHashables())
    def __repr__(self):
        return f'({self.r},{self.g},{self.b}) at ({self.cx}, {self.cy})'
    def __eq__(self, other):
        return isinstance(other, Agar)

    def move(self):
        self.cx += self.dx
        if self.cx - self.radius < self.mode.leftBound:
            self.cx = self.mode.leftBound + self.radius
            self.dx = 0
        elif self.cx + self.radius > self.mode.rightBound:
            self.cx = self.mode.rightBound - self.radius
            self.dx = 0
        
        self.cy += self.dy
        if self.cy - self.radius < self.mode.upperBound:
            self.cy = self.mode.upperBound + self.radius
            self.dy = 0
        elif self.cy + self.radius > self.mode.lowerBound:
            self.cy = self.mode.lowerBound - self.radius
            self.dy = 0
    
    def checkIfCanEat(self, other):
        if (other.radius < self.radius) and \
               (other.cx - other.radius) >= (self.cx - self.radius) and \
               (other.cx + other.radius) <= (self.cx + self.radius) and \
               (other.cy - other.radius) >= (self.cy - self.radius) and \
               (other.cy + other.radius) <= (self.cy + self.radius):
            return True
        else: return False

    

# non-moving objects
class Food(Agar):
    def __init__(self, mode, cx, cy):
        super().__init__(mode, cx, cy)
        self.radius = random.randint(2, 5)
        self.area = math.pi * (self.radius ** 2)
        self.color = rgbString(self.r, self.g, self.b)

    def getHashables(self):
        return (self.r, self.g, self.b)

    def draw(self, canvas, scrollX, scrollY):
        canvas.create_oval(self.cx - self.radius, 
                           self.cy - self.radius, 
                           self.cx + self.radius, 
                           self.cy + self.radius, 
                           fill=self.color, outline='Brown')

class Player(Agar):
    def __init__(self, mode, cx, cy):
        super().__init__(mode, cx, cy)
        self.radius = 10
        self.area = math.pi * (self.radius ** 2)
        self.maxSpeed = (self.area**-1.5) * 10
        self.color = rgbString(255,0,0)
        self.score = self.mode.app.score
    
    def getHashables(self):
        return (self.name,)
    
    def updateArea(self):
        self.area = math.pi * (self.radius ** 2)
        self.mass = self.area / 90
        self.maxSpeed = (self.mass ** -2.5) * 10



    def draw(self, canvas):
        canvas.create_oval(self.cx - self.radius, self.cy - self.radius, 
                           self.cx + self.radius, self.cy + self.radius, fill=self.color)
    
    def eatAgar(self, other):
        newRadius = math.sqrt((self.area + other.area) / math.pi)
        self.radiusQueue += roundHalfUp(newRadius - self.radius)
        self.mode.app.score += other.radius
        self.score = self.mode.app.score
        self.updateArea()

class Enemy(Agar):
    def __init__(self, mode, cx, cy, radius):
        super().__init__(mode, cx, cy)
        self.radius = radius
        self.updateArea()
    
    def getHashables(self):
        return (self.r, self.g, self.b)

    def draw(self, canvas):
        canvas.create_oval(self.cx - self.radius, self.cy - self.radius, 
                           self.cx + self.radius, self.cy + self.radius, fill=self.color)

    def updateArea(self):
        self.area = math.pi * (self.radius ** 2)
        self.mass = self.area / 900
        self.maxSpeed = (self.mass*-1.5) * 10

    # def scaleSpeed(self):
    #     if self.dx != 0 and self.dy != 0:
    #         speed = math.sqrt(self.dx ** 2 + self.dy ** 2)
    #         scale = self.maxSpeed / speed
    #         self.dx *= scale
    #         self.dy *= scale
            

    def changeDir(self):
        self.dx = random.randrange(-1,1)
        self.dy = random.randrange(-1,1)

    def eatAgar(self, other):
        newRadius = math.sqrt((self.area + other.area) / math.pi)
        self.radiusQueue += roundHalfUp(newRadius - self.radius)
        self.updateArea()
        

class AggressiveEnemy(Enemy):
    def __init__(self, mode, cx, cy, radius):
        super().__init__(mode, cx, cy, radius)
        self.color = rgbString(self.r, 0, 0)

    def changeDir(self):
        if self.radius > self.mode.player.radius:
            self.dx = (self.mode.player.cx - self.cx) / (self.mode.width / 4)
            self.dy = (self.mode.player.cy - self.cy) / (self.mode.height / 4)
        else:
            closestSmallerEnemy = None
            closestSmallerEnemyDistance = ''
            for enemy in self.mode.enemies:
                distance = math.sqrt((self.cx + enemy.cx)**2 + (self.cy + enemy.cy)**2)
                if distance > 800: 
                    continue
                elif self.radius <= enemy.radius:
                    continue #checks for larger enemies and if self == enemy
                elif closestSmallerEnemyDistance == '':
                    closestSmallerEnemyDistance = distance
                    closestSmallerEnemy = enemy
                elif distance < closestSmallerEnemyDistance:
                    closestSmallerEnemyDistance = distance
                    closestSmallerEnemy = enemy
            #print(closestSmallerEnemy, closestSmallerEnemyDistance)
            if closestSmallerEnemy == None:
                self.dx = 0
                self.dy = 0
            else:
                self.dx = (closestSmallerEnemy.cx - self.cx) / (self.mode.width / 4)
                self.dy = (closestSmallerEnemy.cy - self.cy) / (self.mode.height / 4)
        #self.scaleSpeed()

class TimidEnemy(Enemy):
    def __init__(self, mode, cx, cy, radius):
        super().__init__(mode, cx, cy, radius)
        self.color = rgbString(0, 0, self.b)

    def changeDir(self):
        if self.radius < self.mode.player.radius:
            self.dx = (self.cx - self.mode.player.cx) / (self.mode.width / 4)
            self.dy = (self.cy - self.mode.player.cy) / (self.mode.height / 4)
        else:
            closestLargerEnemy = None
            closestLargerEnemyDistance = ''
            for enemy in self.mode.enemies:
                distance = math.sqrt((self.cx + enemy.cx)**2 + (self.cy + enemy.cy)**2)
                if distance > 800:
                    continue
                if self.radius >= enemy.radius:
                    continue # skips if other enemy is smaller or same size (includes self)
                #print(distance)
                if closestLargerEnemyDistance == '':
                    closestLargerEnemyDistance = distance
                    closestLargerEnemy = enemy
                elif distance < closestLargerEnemyDistance:
                    closestLargerEnemyDistance = distance
                    closestLargerEnemy = enemy
            #print(closestSmallerEnemy, closestSmallerEnemyDistance)
            if closestLargerEnemy == None:
                self.dx = 0
                self.dy = 0
            else:
                self.dx = (self.cx - closestLargerEnemy.cx) / (self.mode.width / 4)
                self.dy = (self.cy - closestLargerEnemy.cy) / (self.mode.height / 4)
        #self.scaleSpeed()

class PassiveEnemy(Enemy):
    def __init__(self, mode, cx, cy, radius):
        super().__init__(mode, cx, cy, radius)
        self.color = rgbString(0, self.g, 0)

    def changeDir(self):
        if self.radius < self.mode.player.radius:
            self.dx = (self.cx - self.mode.player.cx) / (self.mode.width / 4)
            self.dy = (self.cy - self.mode.player.cy) / (self.mode.height / 4)
        else:
            closestSmallerEnemy = None
            closestSmallerEnemyDistance = ''
            for enemy in self.mode.enemies:
                distance = math.sqrt((self.cx + enemy.cx)**2 + (self.cy + enemy.cy)**2)
                if distance > 300: 
                    continue
                if self.radius <= enemy.radius:
                    continue #checks for larger enemies and if self == enemy
                
                #print(distance)
                elif closestSmallerEnemyDistance == '':
                    closestSmallerEnemyDistance = distance
                    closestSmallerEnemy = enemy
                elif distance < closestSmallerEnemyDistance:
                    closestSmallerEnemyDistance = distance
                    closestSmallerEnemy = enemy
            
            if closestSmallerEnemy == None:
                closestFood = None
                closestFoodDistance = ''
                for food in self.mode.foods:
                    if closestFoodDistance == '':
                        closestFoodDistance = distance
                        closestFood = food
                    elif distance < closestFoodDistance:
                        closestFoodDistance = distance
                        closestFood = food
                self.dx = (closestFood.cx - self.cx) / (self.mode.width / 4)
                self.dy = (closestFood.cy - self.cy) / (self.mode.height / 4)
            else:
                self.dx = (closestSmallerEnemy.cx - self.cx) / (self.mode.width / 4)
                self.dy = (closestSmallerEnemy.cy - self.cy) / (self.mode.height / 4)
        #self.scaleSpeed()