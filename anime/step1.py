import pygame
from pygame.locals import *
import sys

#画面サイズ
SCREEN = Rect(0, 0, 1280, 720)

class Heray(pygame.sprite.Sprite):
    def __init__(self, filename, centerx, dy, angle = 0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename)
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = SCREEN.height/2 - 30
        self.dy = dy
    
    def update(self):
        self.rect.centery += self.dy

        #壁と衝突時の処理(跳ね返り)
        if self.rect.top < 100 or self.rect.bottom > SCREEN.height - 100:
            self.dy = -self.dy

class Herax(pygame.sprite.Sprite):
    def __init__(self, filename, centerx, dx, angle = 0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (200, 100))
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = SCREEN.height/2 - 30
        self.dx = dx
        self.ad_x = 0
    
    def update(self):
        self.rect.centerx += self.dx
        self.ad_x += self.dx

        #壁と衝突時の処理(跳ね返り)
        if self.ad_x == 60 or self.ad_x == -60 :
            self.dx = -self.dx
            self.ad_x = 0

class Syabely(pygame.sprite.Sprite):
    def __init__(self, filename, centerx, dy, angle = 0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (100, 200))
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = SCREEN.height/2 - 30
        self.dy = dy
    
    def update(self):
        self.rect.centery += self.dy

        #壁と衝突時の処理(跳ね返り)
        if self.rect.top < 100 or self.rect.bottom > SCREEN.height - 100:
            self.dy = -self.dy

class Syabelx(pygame.sprite.Sprite):
    def __init__(self, filename, centerx, dx, angle = 0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (200, 100))
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = SCREEN.height/2 - 30
        self.dx = dx
        self.ad_x = 0
    
    def update(self):
        self.rect.centerx += self.dx
        self.ad_x += self.dx

        #壁と衝突時の処理(跳ね返り)
        if self.ad_x == 60 or self.ad_x == -60 :
            self.dx = -self.dx
            self.ad_x = 0
        

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()
    group = pygame.sprite.RenderUpdates()
    Heray.containers = group
    hera = Heray(300, 0 , 4)

    while True:
        screen.fill((0, 0, 0))
        group.update()
        group.draw(screen)

        pygame.display.update()
        clock.tick(60)        

        #イベント処理
        for event in pygame.event.get():
            #システム終了処理
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                exit()

def exit():
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()