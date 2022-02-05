import pygame
from pygame import font
from pygame.locals import *
import sys
import random
import numpy as np

#画面サイズ
SCREEN = Rect(0, 0, 1280, 720)

class Castle(pygame.sprite.Sprite):
    def __init__(self, collider, player):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load('./img/castle.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN.width/2 - 5
        self.rect.centery = SCREEN.height/2 -40
        self.collider = collider
        self.player = player

    def update(self):
        pygame.sprite.spritecollide(self, self.collider, True)

    def Move(self):
        if self.rect.contains(self.player.rect):
            print("中にあるよ")

class Player(pygame.sprite.Sprite):
    images  = []    #画像リスト
    F_POSE = 20     # ポーズフレーム
    F_RATE = 60     # フレームレート
    frame = 0
    flag = 0

    def __init__(self, collider, hp, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)

        #画像パターン格納
        for i in range(0, 3):
            number_str = str(i)
            if len(number_str) == 1:
                number_str = number_str
            self.playerimg = pygame.image.load('./img/player_' + number_str + '.png').convert_alpha()
            self.playerimg = pygame.transform.scale(self.playerimg, (64, 64))
            self.images.append(self.playerimg)
        
        #プレイヤーの初期設定
        self.image = self.images[1]
        self.rect = Rect(0, 0, 40, 60) # 描写範囲(必須)
        self.rect.center = (x, y)
        self.collider = collider
        self.hitpoint = hp

    def update(self):
        #画像の切り替え
        self.image = self.images[int(self.frame / self.F_POSE)]

        if self.flag == 0:
            self.frame += 1
        else:
            self.frame -= 1
        
        #繰り返し
        if self.frame >= len(self.images) * self.F_POSE:
            self.frame = self.F_POSE * 2 - 1
            self.flag = 1
        elif self.frame < 0:
            self.frame = self.F_POSE
            self.flag = 0
        
        if pygame.sprite.spritecollide(self, self.collider, True):
            self.hitpoint.Hit()

class Soldier(pygame.sprite.Sprite):
    images  = []    #画像リスト
    bullets = []

    def __init__(self, x, y, player, player2, castle, castle2):
        pygame.sprite.Sprite.__init__(self, self.containers)

        #画像パターン格納
        for i in range(0, 2):
            number_str = str(i)
            if len(number_str) == 1:
                number_str = number_str
            self.images.append(pygame.image.load('./img/soldier_' + number_str + '.png'))
            self.images[i] = pygame.transform.scale(self.images[i], (150, 200))
        
        #兵士の初期設定
        self.image = self.images[0]
        self.rect = self.image.get_rect() # 描写範囲(必須)
        self.rect.center = (x, y)
        self.dx, self.dy = (np.random.rand(2) - 0.5)*10
        self.velocity = self.dx, self.dy
        self.max_speed = 2
        self.time = 0
        self.player = player
        self.player2 = player2
        self.castle = castle
        self.castle2 = castle2
    
    def update(self):
        self.time += 1
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        self.ax, self.ay = (random.uniform(2, -2), random.uniform(2, -2))
        self.dx += self.ax
        self.dy += self.ay

        if self.rect.centerx < 500 :
            self.image = self.images[0]
        else :
            self.image = self.images[1]
    
        if self.time % 120 == 0:
            self.bullets.append(Bullet())
        for i in range(len(self.bullets)):
            self.bullets[i].Move(self.rect, self.castle, self.castle2)

        #速度制限
        if self.dx > 5 or self.dx < -4:
            self.dx = 1
        elif self.dy > 5 or self.dy < -4:
            self.dy = 1
        
        #壁と衝突時の処理(跳ね返り)
        if self.rect.left < 0 or self.rect.right > SCREEN.width :
            self.dx = -self.dx
        elif self.rect.top < 0 or self.rect.bottom > SCREEN.height:
            self.dy = -self.dy
        
        #壁との衝突時の処理(壁を超えないように)
        self.rect = self.rect.clamp(SCREEN)

        if self.rect.colliderect(self.player.rect):
            self.dx = -self.dx
            self.dy = -self.dy
        
        if self.rect.colliderect(self.player2.rect):
            self.dx = -self.dx
            self.dy = -self.dy
        
        if self.rect.colliderect(self.castle.rect):
            self.dx = -self.dx
            self.dy = -self.dy

class Bullet(pygame.sprite.Sprite):
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        #画像パターン格納
        for i in range(0, 2):
            number_str = str(i)
            if len(number_str) == 1:
                number_str = number_str
            self.images.append(pygame.image.load('./img/tama_' + number_str + '.png'))
            self.images[i] = pygame.transform.scale(self.images[i], (30, 25))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (-20, 0)
        self.state = 'set'
        self.dx = 0

    def Move(self, target, castle, castle2):
        if self.state == 'set':
            if target.centerx < SCREEN.width/2: 
                self.image = self.images[0]
                self.rect.centerx = target.right
                self.rect.centery = target.top + 18
                self.dx = 1
            else :
                self.image = self.images[1]
                self.rect.centerx = target.left - 20
                self.rect.centery = target.top + 18
                self.dx = -1

        self.state = 'shoot'
        if self.state == 'shoot':
            self.rect.centerx += self.dx
            if self.rect.right < 0:
                self.kill()
                self.state = 'set'
            if self.rect.left > SCREEN.width:
                self.kill()
                self.state = 'set'
        
        if self.rect.colliderect(castle.rect):
            self.kill()
        if self.rect.colliderect(castle2.rect):
            self.kill()

class HitPoint():
    def __init__(self, x, y):
        self.font = pygame.font.Font("./myfont/ipag.ttf", 40)
        self.hp = 10
        (self.x, self.y) = (x, y)
    def draw(self, screen):
        text = self.font.render("HP:" + str(self.hp), True, (255, 255, 255))
        screen.blit(text, (self.x, self.y))
    def Hit(self):
        self.hp -= 1

def draw_text(screen, text, size, x, y):
    font = pygame.font.Font("./myfont/ipag.ttf", size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

class Dote():
    def __init__(self) -> None:
        
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN.size)
        self.time = 0
        self.limit_time = 3600
        self.check = "True"
        #描画用のスプライトグループ
        self.group = pygame.sprite.RenderUpdates()
        #衝突判定用のスプライトグループ
        self.collider = pygame.sprite.Group()

        #スプライトグループに追加
        Bullet.containers = self.group, self.collider
        Soldier.containers = self.group
        Player.containers = self.group
        Castle.containers = self.group

        self.Soldiers = []
        self.hitpoint = HitPoint(1000, 560)
        self.hitpoint2 = HitPoint(10, 10)
        self.player = Player(self.collider, self.hitpoint, 400, SCREEN.height/2 - 30)
        self.player2 = Player(self.collider, self.hitpoint2, 800, SCREEN.height/2 - 30)
        self.castle = Castle(self.collider, self.player)
        self.castle2 = Castle(self.collider, self.player2)

        #スタート画面キャラ
        self.intro = pygame.image.load("./img/player_1.png").convert_alpha()
        self.intro = pygame.transform.scale(self.intro, (64, 64))
        self.intro_rect = self.intro.get_rect()
        self.draw_height = [100, SCREEN.height/2, 600]
        self.deadimgs = []
        self.deadimg = pygame.image.load('./img/dashi.png').convert_alpha()

        #１枚の画像を回転させながら８枚格納
        for i in range(8):
            # self.deadimg = pygame.transform.scale(self.deadimg,(95,75))
            self.deadimg = pygame.transform.rotate(self.deadimg,90 * i)
            self.deadimgs.append(self.deadimg)

        self.boulimgs = []
        self.boulimg = pygame.image.load('./img/boul.png').convert_alpha()

        #１枚の画像を回転させながら4枚格納
        for i in range(4):
            self.deadimg = pygame.transform.scale(self.boulimg,(10,10))
            self.boulimg = pygame.transform.rotate(self.boulimg,9 * i)
            self.boulimgs.append(self.boulimg)
    
        self.clock = pygame.time.Clock()

        #フラグ判定
        self.game_start = False
        self.game_play = True
        self.game_over = False
        self.index = 0

    def main(self):
        while True:
            self.screen.fill((0, 0, 0))
            self.clock.tick(60)  #フレームレート60fps

            #説明画面
            if self.game_start:
                self.time += 1
                for i in self.draw_height:
                    self.screen.blit(self.intro, (SCREEN.width/2 - 130, i - 15))
                    draw_text(self.screen, "体力がなくなる前に", 40, SCREEN.width/2 -310, i)
                    draw_text(self.screen, "の周りに土手を作り守れ(1分)", 40, SCREEN.width/2 + 210, i)
                pygame.display.update()
                if self.time == 600:
                    self.game_start = False
                    self.game_play = True

            #実際のアニメーション画面
            if self.game_play:
                self.time += 1
                self.limit_time -= 1
                self.group.update()
                self.group.draw(self.screen)
                self.hitpoint.draw(self.screen)
                self.hitpoint2.draw(self.screen)
                draw_text(self.screen, f"制限時間:{int(self.limit_time/60)}", 40, 990, 600)

                if self.time % 360 == 0 and len(self.Soldiers) < 4:
                    self.Soldiers.append(Soldier(random.randint(0, 700), random.randint(0, 500), self.player, self.castle))

                #画面更新(updateにdirty rectsを渡すとその部分だけ更新するので効率が良い)
                pygame.display.update()

                #城を出す
                if self.check == "True":
                    self.check = "False"
                    self.castle.Move()

                #gameplay終了処理
                if self.hitpoint.hp < 0 or self.limit_time < 0 :
                    self.game_play = False
                    self.time = 0
            
            if self.game_over:
                self.index += 1
                if self.index >= len(self.boulimgs):
                    self.index = 0
                self.boulimg = self.boulimgs[self.index]
                self.clock.tick(3)
                self.screen.blit(self.boulimg, (300 , 200))
                pygame.display.update()

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

# dote = Dote()
# dote.main()