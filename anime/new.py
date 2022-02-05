from typing import Counter
from numpy import angle, radians
import pygame
from pygame.draw import rect
from pygame.locals import *
import sys
import math
import os
import random

os.environ['SDL_VIDEO_WINDOW_POS']= "%d,%d" % (1400,50)
#画面サイズ
SCREEN = Rect(0, 0, 800, 600)

class Monjya(pygame.sprite.Sprite):
    #コンストラクタ(初期化メソッド)
    def __init__(self, filename):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (300, 100))
        self.rect = self.image.get_rect()
        self.rect.centerx = 400
        self.rect.centery = 300
    
    # def update(self):
    #     #魚と衝突したもんじゃを取得
    #     collided = pygame.sprite.spritecollide(self, self.target, True)

class Hera(pygame.sprite.Sprite):
    def __init__(self, filename, x, y, dx, angle, monjya):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert_alpha()
        if angle !=0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.dx = dx
        self.monjya = monjya
        self.radius = self.monjya.rect[3]
        self.x_center = self.monjya.rect[0]+self.monjya.rect[2]/2
        self.y_center = self.monjya.rect[1]+self.monjya.rect[3]/2
        self.count = 0
        self.a = 3.14/360
        self.deg = 0
        self.rad = 0
        self.angle = 0
    
    def update(self):
        Finishtime = pygame.time.get_ticks()
        if(Finishtime < 20000):
            self.sin()    
        elif(20000 <= Finishtime < 40000):
            self.maru()
        elif(40000 <= Finishtime < 50000):
            exit()
        
    def sin(self):
        self.rect.centerx -= self.dx
        self.rect.centery = int(50 * math.sin(math.radians(self.rect.centerx)*6)) + 300
        #壁と衝突時の処理(跳ね返り)
        if self.rect.left < 0 or self.rect.right > SCREEN.width:
            self.dx = -self.dx
        if self.rect.left == self.monjya.rect.right or self.rect.right == self.monjya.rect.left:
            self.dx = -self.dx
        if self.rect.colliderect(self.monjya.rect) and self.dx > 0 or self.monjya.rect.contains(self.rect):
            self.rect.center = (random.randint(100,700),random.randint(100,500))
    
    def maru(self):
        self.angle +=1
        self.count += self.a/3.14
        self.rad += self.count
        self.rect.centerx = int(self.radius * math.cos(self.rad))+self.x_center
        self.rect.centery = int(self.radius * math.sin(self.rad))+self.y_center
        # self.image = pygame.transform.rotate(self.image, random.randint(0,359))
        if self.count >= 3.14/10:
            self.count = 0

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    #描画用のスプライトグループ
    group = pygame.sprite.RenderUpdates()
    #衝突判定用のスプライトグループ
    # collider = pygame.sprite.Group()

    #スプライトグループに追加
    Hera.containers = group
    Monjya.containers = group

    monjya = Monjya("../img/black.png")
    hera = Hera("../img/hera.png", 700, 200, 1, 30, monjya)
    hera2 = Hera("../img/hera.png", 200, 200, 1, 120, monjya)

    clock = pygame.time.Clock()

    #背景の作成と描画(背景は最初の一回だけ描画)
    bg = pygame.Surface(SCREEN.size)
    bg.fill((0, 0, 0))
    screen.blit(bg, (0, 0))
    pygame.display.update()

    while True:
        Finishtime = pygame.time.get_ticks()
        clock.tick(60)  #フレームレート60fps

        group.clear(screen, bg)

        #スプライトグループの更新
        if(Finishtime < 20000):
            hera.sin()
            hera2.sin()    
        elif(20000 <= Finishtime < 40000):
            hera.maru()
            # hera2.maru()
        elif(40000 <= Finishtime < 50000):
            exit()

        dirty_rects = group.draw(screen)

        #画面更新(updateにdirty rectsを渡すとその部分だけ更新するので効率が良い)
        pygame.display.update(dirty_rects)

        #イベント処理
        for event in pygame.event.get():
            #終了処理
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                exit()

def exit():
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()