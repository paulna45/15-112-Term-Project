from tkinter import *
from PIL import Image, ImageTk
import random

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

    def move(self):
        self.cy += self.dy
        self.cx += self.dx
    
    def checkIfCanEat(self, other):
        return (other.radius < self.radius * 1.2) and \
               (other.cx - other.radius) >= (self.cx - self.radius) and \
               (other.cx + other.radius) <= (self.cx + self.radius) and \
               (other.cy - other.radius) >= (self.cy - self.radius) and \
               (other.cy + other.radius) <= (self.cy + self.radius)

    def eatAgar(self, other):
        self.radius += other.radius
        if isinstance(other, Enemy):
            self.mode.enemies.remove(other)

class Player(Agar):
    def __init__(self, mode, cx, cy):
        super().__init__(mode, cx, cy)
        self.radius = 10
        self.color = rgbString(255,0,0)
    
    def getHashables(self):
        return (self.name,)
    
    def draw(self, canvas):
        canvas.create_oval(self.cx - self.radius, self.cy - self.radius, 
                           self.cx + self.radius, self.cy + self.radius, fill=self.color)

class Enemy(Agar):
    def __init__(self, mode, cx, cy, radius):
        super().__init__(mode, cx, cy)
        self.radius = radius
    
    def getHashables(self):
        return (self.r, self.g, self.b)

    def draw(self, canvas):
        canvas.create_oval(self.cx - self.radius, self.cy - self.radius, 
                           self.cx + self.radius, self.cy + self.radius, fill=self.color)
