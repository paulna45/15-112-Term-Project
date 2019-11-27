# cmu_112_graphics retrieved from http://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *
from tkinter import *
from PIL import Image, ImageTk
from AgarObjects import *
import math, random, sys

class AgarioGame(ModalApp):
    def appStarted(app):
        app.timerDelay = 30 # milliseconds
        app.splashScreenMode = SplashScreenMode()
        app.gameMode = GameMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)

        
class GameMode(Mode):
    def appStarted(mode):
        mode.score = 0
        mode.spawnTimeInterval = 200 # times 30 milliseconds == 6 second interval
        mode.timeInt = 0
        mode.cx = mode.width//2
        mode.cy = mode.height//2
        mode.player = Player(mode, mode.cx, mode.cy)

        mode.enemies = set()
        for _ in range(20):
            mode.createEnemy()

    def createEnemy(mode):
        cx = random.randint(15, 2000)
        cy = random.randint(15, 2000)
        r = random.randint(8,12)
        enemy = Enemy(mode, cx, cy, r)
        mode.enemies.add(enemy)

    def timerFired(mode):
        if mode.timeInt % mode.spawnTimeInterval == 0:
            mode.createEnemy()
        mode.player.move()
        for enemy in mode.enemies:
            if mode.player.checkIfCanEat(enemy):
                mode.player.eatAgar(enemy)
            
        mode.timeInt += 1

        #for enemy in mode.enemies:
        #    enemy.move()

    def keyPressed(mode, event):
        if event.key in ['Left', 'A']:
            mode.player.dx -= 1
        elif event.key in ['Up', 'W']:
            mode.player.dy -= 1
        elif event.key in ['Right', 'D']:
            mode.player.dx += 1
        elif event.key in ['Down', 'S']:
            mode.player.dy += 1
    
    def mouseMoved(mode, event):
        x, y = event.x, event.y
        d = math.sqrt((mode.cx + x) ** 2 + (mode.cy + y) ** 2)
        mode.player.dx = (x - mode.cx) / mode.width
        mode.player.dy = (y - mode.cy) / mode.height

    def redrawAll(mode, canvas):
        mode.player.draw(canvas)
        for enemy in mode.enemies:
            enemy.draw(canvas)

class SplashScreenMode(Mode):
    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)

class HelpMode(Mode):
    pass

def main():
    AgarioGame(width=960,height=600)

if __name__ == '__main__':
    main()

