import pygame
from pygame.locals import *
import sys

#画面サイズ
SCREEN = Rect(0, 0, 800, 600)

class Fighter(pygame.sprite.Sprite):
    #コンストラクタ(初期化メソッド)
    def __init__(self, filename, x, y, sx, sy, angle=0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (sx, sy))
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Img(pygame.sprite.Sprite):
    #コンストラクタ(初期化メソッド)
    def __init__(self, filename, x, y, sx, sy, angle=0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (sx, sy))
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Image(pygame.sprite.Sprite):
    #コンストラクタ(初期化メソッド)
    def __init__(self, filename):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename)
        self.rect = self.image.get_rect()
        # self.rect.center = (x, y)

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()
    #描画用のスプライトグループ
    group = pygame.sprite.RenderUpdates()
    group2 = pygame.sprite.RenderUpdates()
    group3 = pygame.sprite.RenderUpdates()
    Fighter.containers = group
    Img.containers = group2
    Image.containers = group3

    fires = []
    for i in range(8):
        number_str = str(i)
        if len(number_str) == 1:
            number_str = number_str
        fires.append(pygame.image.load('../img/flame_parts_' + number_str + '.png'))
        fires[i] = pygame.transform.scale(fires[i], (200, 200))
    fireimg = fires[0]
    index = 0

    fighter1 = Fighter("../img/firefighter01.png", 600, 200, 200, 180)
    fighter2 = Fighter("../img/firefighter02.png", 400, 400, 200, 180)
    mark1 = Img("../img/mark01.png", 700, 100, 200, 200)
    mark2 = Img("../img/mark02.png", 100, 500, 200, 200)
    koji1 = Img("../img/koji01.png", 400, 300, 400, 350)
    bg = Image("../img/dog.jpg")

    dashi_start = False
    dashi_stop = False
    step1 = True

    while True:
        if dashi_start:
            pygame.display.update()
            clock.tick(10)
            screen.fill((0, 0, 0))
            screen.blit(fireimg, (0, 0))
            index += 1
            if index >= len(fires):
                index = 0
            fireimg = fires[index]
            group.draw(screen)
        
        if dashi_stop:
            pygame.display.update()
            clock.tick(10)
            screen.fill((0, 0, 0))
            group2.draw(screen)
        
        if step1:
            pygame.display.update()
            clock.tick(10)
            screen.fill((0, 0, 0))
            group3.draw(screen)


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