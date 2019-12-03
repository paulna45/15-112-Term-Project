# cmu_112_graphics retrieved from http://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *
from tkinter import *
from PIL import Image, ImageTk
from AgarObjects import *
import math, random, sys, decimal 

# from https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html#HelperFunctions
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

class GelioGame(ModalApp):
    def appStarted(app):
        app.timerDelay = 30 # milliseconds
        app.score = 0
        app.splashScreenMode = SplashScreenMode()
        app.gameMode = GameMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)

        
class GameMode(Mode):
    def appStarted(mode):
        mode.spawnTimeInterval = 100 # times 30 milliseconds == 3 second interval
        mode.timeInt = 0
        mode.scrollX = 0
        mode.scrollXRate = 0
        mode.scrollYRate = 0
        mode.scrollY = 0
        mode.cx = mode.width//2
        mode.cy = mode.height//2

        mode.leftBorder = -1440
        mode.leftBound = -1440
        mode.rightBorder = 2400
        mode.rightBound = 2400
        mode.upperBorder = -900
        mode.upperBound = -900
        mode.lowerBorder = 1500
        mode.lowerBound = 1500

        mode.player = Player(mode, mode.cx, mode.cy)
        mode.allObjects = set()
        mode.enemies = set()
        for _ in range(20):
            mode.createEnemy()

    def createEnemy(mode):
        cx = random.randint(15, 1000)
        cy = random.randint(15, 1000)
        lo = roundHalfUp(mode.player.radius * 0.8)
        hi = roundHalfUp(mode.player.radius * 1.2)
        r = random.randint(lo, hi)
        x = random.randint(0,1)
        if x == 0:
            enemy = AggressiveEnemy(mode, cx, cy, r)
        elif x == 1:
            enemy = TimidEnemy(mode, cx, cy, r)
        mode.enemies.add(enemy)
        mode.allObjects.add(enemy)

    def timerFired(mode):
        if mode.timeInt % mode.spawnTimeInterval == 0:
            mode.createEnemy()
        mode.scrollXRate = mode.player.dx
        mode.scrollYRate = mode.player.dy

        #update cx & cy for all non-Player objects, for sidescrolling
        for thing in mode.allObjects:
            thing.cx -= mode.scrollXRate
            thing.cy -= mode.scrollYRate
        # keeps track of total amount scrolled
        mode.scrollX += mode.scrollXRate
        mode.scrollY += mode.scrollYRate

        # updates bounds
        mode.leftBound = mode.leftBorder - mode.scrollX
        mode.rightBound = mode.rightBorder - mode.scrollX
        mode.upperBound = mode.upperBorder - mode.scrollY
        mode.lowerBound = mode.lowerBorder - mode.scrollY

        deadEnemies = set() # keeps track of dead enemies
        # changes movement of enemies
        for enemy in mode.enemies:
            enemy.changeDir()
            enemy.move()
            for other in mode.enemies:
                if enemy == other:
                    continue
                elif enemy.checkIfCanEat(other):
                    if enemy.radius == other.radius: continue
                    elif enemy.radius > other.radius:
                        enemy.eatAgar(other)
                        deadEnemies.add(other)
                    elif other.radius > enemy.radius:
                        other.eatAgar(enemy)
                        deadEnemies.add(enemy)

        for enemy in mode.enemies: #keeps track of dead enemies
            if mode.player.checkIfCanEat(enemy):
                mode.player.eatAgar(enemy)
                deadEnemies.add(enemy)
        for enemy in deadEnemies:
            mode.enemies.remove(enemy)
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
        mode.player.dx = (x - mode.cx) / (mode.width / 4)
        mode.player.dy = (y - mode.cy) / (mode.height / 4)

    def drawGrid(mode, canvas):
        for x in range(math.floor(mode.leftBound), math.ceil(mode.rightBound) + 1, 30):
            canvas.create_line(x + mode.leftBound%1, mode.upperBound, 
                               x + mode.leftBound%1, mode.lowerBound)
        for y in range(math.floor(mode.upperBound), math.ceil(mode.lowerBound) + 1, 30):
            canvas.create_line(mode.leftBound, y + mode.upperBound%1, 
                               mode.rightBound, y + mode.upperBound%1)

    def drawScore(mode, canvas):
        canvas.create_text(mode.width, mode.height, text=f'Score: {mode.app.score}')

    def redrawAll(mode, canvas):
        mode.drawGrid(canvas)
        for enemy in mode.enemies:
            enemy.draw(canvas)
        mode.player.draw(canvas)
        mode.drawScore(canvas)

class SplashScreenMode(Mode):
    def appStarted(mode):
        mode.leftBound = 0
        mode.rightBound = int(mode.width)
        mode.upperBound = 0
        mode.lowerBound = int(mode.height)
    
    def drawGrid(mode, canvas):
        for x in range(mode.leftBound, mode.rightBound + 1, 30):
            canvas.create_line(x, mode.upperBound, 
                               x, mode.lowerBound, fill='Grey')
        for y in range(mode.upperBound, mode.lowerBound + 1, 30):
            canvas.create_line(mode.leftBound, y, 
                               mode.rightBound, y, fill='Grey')

    def drawLogo(mode, canvas):
        canvas.create_text(mode.width/2, mode.height/4, text='GEL.io', font=('Comic Sans MS', 80, 'bold'))

    def drawStartButton(mode, canvas):
        canvas.create_rectangle(mode.width/4, mode.height/2 + 10, 
                                mode.width*3/4, mode.height*3/4 - 10, 
                                fill='Green', activefill='Yellow')
        canvas.create_text(mode.width/2, mode.height*5/8, text='PLAY!', font='Arial 50 bold')
    
    def drawHelpButton(mode, canvas):
        canvas.create_rectangle(mode.width/3, mode.height*3/4, 
                                mode.width*2/3, mode.height*11/12, 
                                fill='Orange', activefill='Red')
        canvas.create_text(mode.width/2, mode.height*5/6, text='HELP', font='Arial 40 bold')

    def mousePressed(mode, event):
        if event.x > mode.width/4 and event.x < mode.width*3/4 and \
           event.y > mode.height/2 + 10 and event.y < mode.height*3/4 - 10:
            mode.app.setActiveMode(mode.app.gameMode)
        elif event.x > mode.width/3 and event.x < mode.width*2/3 and \
             event.y > mode.height*4/5 and event.y < mode.height*11/12:
            mode.app.setActiveMode(mode.app.helpMode)

    def redrawAll(mode, canvas):
        mode.drawGrid(canvas)
        mode.drawLogo(canvas)
        mode.drawStartButton(canvas)
        mode.drawHelpButton(canvas)

class HelpMode(Mode):
    def mousePressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)

def main():
    GelioGame(width=960,height=600)

if __name__ == '__main__':
    main()