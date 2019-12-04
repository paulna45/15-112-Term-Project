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

    def eatAgar(self, other):
        self.radius += roundHalfUp(math.sqrt(other.radius))

class Blob(Agar):
    def __init__(self, mode, cx, cy):
        super().__init__(mode, cx, cy)
        self.radius = random.randint(2, 5)
        self.color = rgbString(self.r, self.g, self.b)

    def getHashables(self):
        return (self.cx, self.cy)

    def draw(self, canvas):
        canvas.create_oval(self.cx - self.radius, self.cy - self.radius, 
                           self.cx + self.radius, self.cy + self.radius, 
                           fill=self.color, outline='Yellow')

class Player(Agar):
    def __init__(self, mode, cx, cy):
        super().__init__(mode, cx, cy)
        self.radius = 10
        self.color = rgbString(255,0,0)
        self.score = self.mode.app.score
    
    def getHashables(self):
        return (self.name,)
    
    def draw(self, canvas):
        canvas.create_oval(self.cx - self.radius, self.cy - self.radius, 
                           self.cx + self.radius, self.cy + self.radius, fill=self.color)
    
    def eatAgar(self, other):
        self.radius += roundHalfUp(math.sqrt(other.radius))
        self.mode.app.score += other.radius
        self.score = self.mode.app.score

class Enemy(Agar):
    def __init__(self, mode, cx, cy, radius):
        super().__init__(mode, cx, cy)
        self.radius = radius
    
    def getHashables(self):
        return (self.r, self.g, self.b)

    def draw(self, canvas):
        canvas.create_oval(self.cx - self.radius, self.cy - self.radius, 
                           self.cx + self.radius, self.cy + self.radius, fill=self.color)

    def changeDir(self):
        self.dx = random.randrange(-1,1)
        self.dy = random.randrange(-1,1)

    #def move(self):
        

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
                if self.radius <= enemy.radius:
                    continue #checks for larger enemies and if self == enemy
                distance = math.sqrt((self.cx + enemy.cx)**2 + (self.cy + enemy.cy)**2)
                #print(distance)
                if closestSmallerEnemyDistance == '':
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
                if self.radius >= enemy.radius:
                    continue # skips if other enemy is smaller or same size (includes self)
                distance = math.sqrt((self.cx + enemy.cx)**2 + (self.cy + enemy.cy)**2)
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

class PassiveEnemy(Enemy):
    def __init__(self, mode, cx, cy, radius):
        super().__init__(mode, cx, cy, radius)
        self.color = rgbString(0, self.g, 0)

    def changeDir(self):
        if self.radius < self.mode.player.radius:
            self.dx = (self.cx - self.mode.player.cx) / (self.mode.width / 4)
            self.dy = (self.cy - self.mode.player.cy) / (self.mode.height / 4)
        else:
            closestLargerEnemy = None
            closestLargerEnemyDistance = ''
            for enemy in self.mode.enemies:
                if self.radius >= enemy.radius:
                    continue #checks for smaller enemies and if self == enemy
                distance = math.sqrt((self.cx + enemy.cx)**2 + (self.cy + enemy.cy)**2)
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