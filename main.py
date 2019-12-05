# The main executable file.

# cmu_112_graphics retrieved from http://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *
from tkinter import *
from PIL import Image, ImageTk
from Objects import *
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
        app.gameOverMode = GameOverMode()
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
        mode.foods = set()
        for _ in range(100):
            mode.createFood()
        for _ in range(20):
            mode.createEnemy()

    def createFood(mode):
        cx = random.randint(-1435 - roundHalfUp(mode.scrollX), -435 - roundHalfUp(mode.scrollX))
        cy = random.randint(-895 - roundHalfUp(mode.scrollY), 1495 - roundHalfUp(mode.scrollY))
        food = Food(mode, cx, cy)
        mode.allObjects.add(food)
        mode.foods.add(food)
        

    def createEnemy(mode):
        cx = random.randint(15 - roundHalfUp(mode.scrollX), 1000 - roundHalfUp(mode.scrollX))
        cy = random.randint(15 - roundHalfUp(mode.scrollY), 1000 - roundHalfUp(mode.scrollY))
        while ((cx + mode.player.radius*1.2) <= mode.player.cx + mode.player.radius) and \
              ((cx + mode.player.radius*1.2) >= mode.player.cx - mode.player.radius) and \
              ((cy + mode.player.radius*1.2) <= mode.player.cy + mode.player.radius) and \
              ((cy + mode.player.radius*1.2) >= mode.player.cy - mode.player.radius):
            cx = random.randint(15 - mode.scrollX, 1000 - mode.scrollX)
            cy = random.randint(15 - mode.scrollY, 1000 - mode.scrollY)
        lo = (roundHalfUp(mode.player.radius * 0.8))
        hi = (roundHalfUp(mode.player.radius * 1.2))
        print(lo, hi)
        try:
            r = random.randint(lo, hi)
        except: pass
        x = random.randint(0,2)
        if x == 0:
            enemy = AggressiveEnemy(mode, cx, cy, r)
        elif x == 1:
            enemy = TimidEnemy(mode, cx, cy, r)
        elif x == 2:
            enemy = PassiveEnemy(mode, cx, cy, r)
        mode.enemies.add(enemy)
        mode.allObjects.add(enemy)

    def timerFired(mode):
        #creates new food and enemies
        mode.createFood()
        if mode.timeInt % mode.spawnTimeInterval == 0:
            mode.createEnemy()
        
        # sidescrolling
        mode.scrollXRate = mode.player.dx
        mode.scrollYRate = mode.player.dy

        # Smooth change of radii
        # Player:
        if mode.player.radiusQueue > 0:
            mode.player.radiusQueue -= 1
            mode.player.radius += 1
        # Enemies
        for thing in mode.enemies:
            if thing.radiusQueue > 0:
                thing.radiusQueue -= 1
                thing.radius += 1

        # Update cx & cy for all enemies, for sidescrolling
        for thing in mode.enemies:
            thing.cx -= mode.scrollXRate
            thing.cy -= mode.scrollYRate
        # Update cx & cy for food, for sidescrolling
        for food in mode.foods:
            food.cx -= mode.scrollXRate
            food.cy -= mode.scrollYRate
        # keeps track of total amount scrolled
        mode.scrollX += mode.scrollXRate
        mode.scrollY += mode.scrollYRate

        # updates bounds
        mode.leftBound = mode.leftBorder - mode.scrollX
        mode.rightBound = mode.rightBorder - mode.scrollX
        mode.upperBound = mode.upperBorder - mode.scrollY
        mode.lowerBound = mode.lowerBorder - mode.scrollY      

        deadEnemies = set() # keeps track of dead enemies
        deadFood = set() #keeps track of 'dead' food
        # changes movement of enemies
        for enemy in mode.enemies:
            enemy.changeDir()
            enemy.move()
            for food in mode.foods:
                if enemy.checkIfCanEat(food):
                    enemy.eatAgar(food)
                    deadFood.add(food)
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

        for enemy in mode.enemies:
            if mode.player.checkIfCanEat(enemy):
                mode.player.eatAgar(enemy)
                deadEnemies.add(enemy)
        for food in mode.foods:
            if mode.player.checkIfCanEat(food):
                mode.player.eatAgar(food)
                deadFood.add(food)
        #removes eaten objects from set
        for enemy in deadEnemies:
            mode.enemies.remove(enemy)
        for food in deadFood:
            mode.foods.remove(food)
        mode.timeInt += 1

        #checks if player is eaten
        for enemy in mode.enemies:
            if enemy.checkIfCanEat(mode.player):
                mode.app.setActiveMode(mode.app.gameOverMode)

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
        scale = 1

        mode.player.dx = (x - mode.cx) * scale / (mode.width / 9)
        mode.player.dy = (y - mode.cy) * scale / (mode.height / 9)

    def drawGrid(mode, canvas):
        for x in range(math.floor(mode.leftBound), math.ceil(mode.rightBound) + 1, 30):
            canvas.create_line(x + mode.leftBound%1, mode.upperBound, 
                               x + mode.leftBound%1, mode.lowerBound)
        for y in range(math.floor(mode.upperBound), math.ceil(mode.lowerBound) + 1, 30):
            canvas.create_line(mode.leftBound, y + mode.upperBound%1, 
                               mode.rightBound, y + mode.upperBound%1)

    def drawScore(mode, canvas):
        canvas.create_text(0, mode.height, 
                           text=f'Score: {mode.app.score}', anchor='sw')

    def drawFood(mode, canvas):
        for food in mode.foods:
            food.draw(canvas, mode.scrollX, mode.scrollY)

    def drawEnemies(mode, canvas):
        for enemy in mode.enemies:
            enemy.draw(canvas)

    def redrawAll(mode, canvas):
        mode.drawGrid(canvas)
        mode.drawFood(canvas)
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
        canvas.create_text(mode.width/2, mode.height/4, text='GEL.io', 
                           font=('Comic Sans MS', 80, 'bold'))

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

class GameOverMode(Mode):
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

    def drawStartButton(mode, canvas):
        canvas.create_rectangle(mode.width/4, mode.height*3/8 + 10, 
                                mode.width*3/4, mode.height*5/8 - 10, 
                                fill='Green', activefill='Yellow')
        canvas.create_text(mode.width/2, mode.height/2, text='Play Again?', font='Arial 40 bold')

    def showScore(mode, canvas):
        canvas.create_text(mode.width/2, mode.height/8, text='Your Score:',
                           font='Arial 30')
        canvas.create_text(mode.width/2, mode.height/4, text=f'{mode.app.score}',
                           font=('Comic Sans MS', 50, 'bold'))

    def mousePressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)

    def redrawAll(mode, canvas):
        mode.drawGrid(canvas)
        mode.showScore(canvas)
        mode.drawStartButton(canvas)

def main():
    GelioGame(width=960,height=600)

if __name__ == '__main__':
    main()