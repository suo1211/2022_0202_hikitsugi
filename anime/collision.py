import time
import pygame
from pygame.locals import *
import sys


#画面サイズ
SCREEN = Rect(0, 0, 800, 600)

#もんじゃ焼きの位置のクラス
class Monjya(pygame.sprite.Sprite):
    #コンストラクタ(初期化メソッド)
    def __init__(self, filename, target, screen):
        # x1, y1, w, h = ellipse()s
        # print(w,h)
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (350, 200))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN.width/2, SCREEN.height/2)
        # self.rect = Rect(x1, y1, w/2, h/2)
        self.target = target
        self.screen = screen
    
    # def update(self):
    #     #魚と衝突したもんじゃを取得
    #     collided = pygame.sprite.spritecollide(self, self.target, True)

class Fish(pygame.sprite.Sprite):
    #コンストラクタ(初期メソッド)
    def __init__(self, filename, xy, vxy, angle_left, angle_right):
        x, y = xy
        vx, vy = vxy
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.dx = vx
        self.dy = vy
        self.angel_left = angle_left
        self.angel_right = angle_right
    
    def update(self):
        self.rect.centerx += self.dx
        self.rect.centery += self.dy

        #壁と衝突時の処理(跳ね返り)
        if self.rect.left < 0 or self.rect.right > SCREEN.width:
            self.dx = -self.dx
        if self.rect.top < 0 or self.rect.bottom > SCREEN.height:
            self.dy = -self.dy
        #壁との衝突時の処理(壁を超えないように)
        self.rect = self.rect.clamp(SCREEN)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)

    #描画用のスプライトグループ
    group = pygame.sprite.RenderUpdates()
    #衝突判定用のスプライトグループ
    collider = pygame.sprite.Group()

    #スプライトグループに追加
    Monjya.containers = group
    Fish.containers = group, collider

    #もんじゃの作成
    monjya = Monjya("../img/hamada.jpg", collider, screen)
    fish = Fish("../img/fish.png", (600, 400), (2, 4), 0, 0)

    clock = pygame.time.Clock()
    #背景の作成と描画(背景は最初の一回だけ描画)
    bg = pygame.Surface(SCREEN.size)
    bg.fill((0, 0, 0))
    screen.blit(bg, (0, 0))
    pygame.display.update()

    while True:
        clock.tick(60)  #フレームレート60fps
        group.clear(screen, bg)
        #スプライトグループの更新
        group.update()
        #スプライトを更新
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