from pygame import *
import math as m
from random import random

w, h = 700, 500
window = display.set_mode((w, h)) 
sprites = []
enemies = []
movable = []
clock = time.Clock()
game = True
finish = False
lastID = -1
bulletCache = []
bulletActive = {}

mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
fire = mixer.Sound("fire.ogg")

class GameSprite(sprite.Sprite):
    def __init__(s, x, y, sx, sy, img, vel = [0, 0], addToSprites = True):
        super().__init__()
        s.x = w*x
        s.y = h*y
        s.sx = int(w*sx)
        s.sy = int(h*sy)
        s.img = transform.scale(image.load(img), (s.sx, s.sy))
        s.rect = s.img.get_rect()
        s.vel = vel
        if addToSprites:
            sprites.append(s)
    def draw(s):
        window.blit(s.img, (s.x, s.y))

class Bullet(GameSprite):
    def __init__(s, player):
        global lastID
        super().__init__(0, 0, 0.03125, 0.07, "bullet.png", [0, -6], False)
        s.x = player.x+player.sx/2
        s.y = player.y
        s.velLimited = False
        s.ID = lastID + 1
        s.plr = player
        bulletActive[s.ID] = s
        lastID += 1
    def checkCollision(s, wall):
        if (s.x+s.sx > wall.x and s.x < wall.x+wall.sx) and (s.y+s.sy > wall.y and s.y < wall.y+wall.sy):
            return True
        else:
            return False
    def reuseBullet(s):
        s.x = s.plr.x+s.plr.sx/2
        s.y = s.plr.y
        bulletActive[s.ID] = s

def shoot():
    global plr, fire
    fire.play()
    l = len(bulletCache)
    if l != 0 and bulletCache[l-1]:
        bulletCache[l-1].reuseBullet()
        del bulletCache[l-1]
    else:
        Bullet(plr)

class Player(GameSprite):
    def __init__(s, x, y):
        super().__init__(x, y, 0.1, 0.14, "rocket.png")
        s.velLimited = True
        movable.append(s)

    def move(s, k):
        vel = [0, 0]
        if k[K_RIGHT]:
            vel[0] += 1
        if k[K_LEFT]:
            vel[0] += -1
        if vel[0] == 0 and vel[1] == 0:
            return
        else:
            n = m.sqrt(vel[0]**2 + vel[1]**2)
            s.vel = (s.vel[0] + vel[0]/n*0.4, s.vel[1] + vel[1]/n*0.4)
    
    def checkCollision(s, wall):
        if (s.x+s.sx > wall.x and s.x < wall.x+wall.sx) and (s.y+s.sy > wall.y and s.y < wall.y+wall.sy):
            return True
        else:
            return False

class Enemy(GameSprite):
    def __init__(s, x, y):
        super().__init__(x, y, 0.1, 0.14, "ufo.png")
        s.velLimited = False
        s.speed = random()-0.5
        s.yspeed = 0.25 + random()*0.25
        movable.append(s)
        enemies.append(s)
    def respawn(s):
        s.x = w*random()
        s.y = 0
        s.speed = random()-0.5
        s.yspeed = 0.25 + random()*0.25


bg = GameSprite(0, 0, 1, 1, "galaxy.jpg")

plr = Player(0.55, 1)

for i in range(5):
    Enemy(random(), 0)

font.init()
font = font.SysFont("Arial", 32)
scoreT = font.render('Счет: 0', True, (255, 255, 255))
missedT = font.render('Пропущено: 0', True, (255, 255, 255))
winT = font.render('Вы выиграли', True, (255, 215, 0))
loseT = font.render('Вы проиграли', True, (255, 215, 0))
scoreN = 0
missedN = 0

def updateText():
    global scoreT, missedT, scoreN, missedN
    scoreT = font.render('Счет: '+str(scoreN), True, (255, 255, 255))
    missedT = font.render('Пропущено: '+str(missedN), True, (255, 255, 255))


def ending(win):
    global game
    if win:
        window.blit(winT, (w/2-32, h/2-32))
    else:
        window.blit(loseT, (w/2-32, h/2-32))
    display.update()
    game = False
    clock.tick(1/5)

t = 0
while game:
    clock.tick(60)

    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN and key.get_pressed()[K_SPACE]:
            shoot()

    plr.move(key.get_pressed())
    todel = []

    t += 1/60
    for enemy in enemies:
        enemy.vel = [m.sin(t*3.1415*enemy.speed), (1 + m.cos(t*6.283*enemy.speed)/2)*enemy.yspeed]
        if enemy.y > h:
            enemy.respawn()
            missedN += 1
            updateText()
        if plr.checkCollision(enemy):
            ending(False)
        for b in bulletActive.values():
            if b.checkCollision(enemy):
                enemy.respawn()
                todel.append(b.ID)
                bulletCache.append(b)
                scoreN += 1
                updateText()

    for b in bulletActive.values():
        if b.y < 0 and not b.ID in todel:
            todel.append(b.ID)
            bulletCache.append(b)
    for id in todel:
        try: del bulletActive[id]
        except: print("")

    bullets = []
    for bul in bulletActive.values():
        bullets.append(bul)

    for obj in (movable + bullets):
        if obj.velLimited:
            obj.x = max(min(obj.x + obj.vel[0], w*0.9), 0)
            obj.y = max(min(obj.y + obj.vel[1], h*0.86), 0)
            obj.vel = [obj.vel[0]*0.95, obj.vel[1]*0.95]
        else:
            obj.x = max(min(obj.x + obj.vel[0], w*0.9), 0)
            obj.y += obj.vel[1]

    for sprite in (sprites + bullets):
        sprite.draw()
    window.blit(scoreT, (0, 16))
    window.blit(missedT, (0, 48))

    if missedN >= 3:
        ending(False)
    if scoreN >= 10:
        ending(True)

    display.update()
