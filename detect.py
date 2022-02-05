# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Run inference on images, videos, directories, streams, etc.

Usage:
    $ python path/to/detect.py --weights yolov5s.pt --source 0  # webcam
                                                             img.jpg  # image
                                                             vid.mp4  # video
                                                             path/  # directory
                                                             path/*.jpg  # glob
                                                             'https://youtu.be/Zgi9g1ksQHc'  # YouTube
                                                             'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream
"""

import argparse
import os
import sys
from pathlib import Path
from typing import cast

import cv2
from pygame.display import Info
import torch
import torch.backends.cudnn as cudnn
import threading
import pygame
import time
import math
import random


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams, dataset_stats
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,user_config_dir,
                           increment_path, non_max_suppression, print_args, scale_coords, is_ascii, is_chinese, xyxy2xywh)
from utils.plots import colors, save_one_box
from utils.torch_utils import select_device, time_sync
from realsense_camera import *
from pygame.locals import *
from PIL import Image, ImageDraw, ImageFont
from anime.heisi import Player, Soldier, Bullet, HitPoint, draw_text
from anime.Fire import Fighter, Img, Image
from anime.step1 import Heray, Herax, Syabelx, Syabely
# Settings
RANK = int(os.getenv('RANK', -1))
CONFIG_DIR = user_config_dir()  # Ultralytics settings dir

#画面サイズ
SCREEN = Rect(0, 0, 1280, 720)

class Castle(pygame.sprite.Sprite):
    def __init__(self, collider, player, Rectswitch):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load('./img/castle.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = -100
        self.rect.centery = 0
        self.collider = collider
        self.player = player
        self.time = 0
        self.game_clear = False
        self.Rectswitch = Rectswitch

    def Move(self):
        if self.Rectswitch in globals():
            if self.Rectswitch == "Rect_Info_2":
                xy, x2y2, = Rect_Info_2
            else:
                xy, x2y2, = Rect_Info
            self.x, self.y = xy
            self.x2, self.y2 = x2y2
            
            self.w = self.x2 - self.x
            self.h = self.y2 - self.y
            self.image = pygame.transform.scale(self.image, (self.w + 50, self.h + 50))
            self.rect = Rect(self.x, self.y, self.w, self.h)
            if self.rect.collidepoint(self.player.rect.centerx, self.player.rect.centery):
                self.rect.center = (self.player.rect.centerx, self.player.rect.centery)
                self.time += 1
                if self.time == 600:
                    self.game_clear = True
            else :
                self.rect.center = (-1000, -1000)
        
        return self.game_clear

class Fire():
    fires = []
    def __init__(self, Rectswitch):
        for i in range(8):
            number_str = str(i)
            if len(number_str) == 1:
                number_str = number_str
            self.img = pygame.image.load('./img/flame_parts_' + number_str + '.png')
            self.img = pygame.transform.scale(self.img, (700, 700))
            self.fires.append(self.img)
        self.fireimg = self.fires[0]
        self.index = 0
        self.Rectswitch = Rectswitch

    def update(self, screen):
        self.index += 1
        if self.index >= len(self.fires):
            self.index = 0
        self.fireimg = self.fires[self.index]
        if self.Rectswitch == "Rect_Info_2":
            xy, x2y2, = Rect_Info_2
            self.x, self.y = xy
            self.x2, self.y2 = x2y2
            self.w = self.x2 - self.x
            self.h = self.y2 - self.y
            self.centerx, self.centery = (self.x - self.w/2 - 20, SCREEN.height/2 - 350)
        elif self.Rectswitch == "Rect_Info":
            xy, x2y2, = Rect_Info
            self.x, self.y = xy
            self.x2, self.y2 = x2y2
            self.w = self.x2 - self.x
            self.h = self.y2 - self.y
            self.centerx, self.centery = (self.x - self.w/2 - 180, SCREEN.height/2 - 350)
        screen.blit(self.fireimg, (self.centerx, self.centery))   

def ProjectM():
    os.environ['SDL_VIDEO_WINDOW_POS']= "%d,%d" % (2400,150)
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    font = pygame.font.Font("./myfont/ipag.ttf", 50)
    time = 0
    limit_time = 3600
    #描画用のスプライトグループ
    group = pygame.sprite.RenderUpdates()
    group1 = pygame.sprite.RenderUpdates()
    group2 = pygame.sprite.RenderUpdates()
    group3 = pygame.sprite.RenderUpdates()
    group4 = pygame.sprite.RenderUpdates()
    group5 = pygame.sprite.RenderUpdates()
    group6 = pygame.sprite.RenderUpdates()
    group7 = pygame.sprite.RenderUpdates()
    #衝突判定用のスプライトグループ
    collider = pygame.sprite.Group()

    #スプライトグループに追加
    Bullet.containers = group, collider
    Soldier.containers = group
    Player.containers = group
    Castle.containers = group
    Heray.containers = group1
    Herax.containers = group4
    Fighter.containers = group2
    Img.containers = group3
    Syabely.containers = group6
    Syabelx.containers = group7

    hera1 = Heray("./img/hera.png", 400, 5)
    hera2 = Heray("./img/hera2.png", 200, -5)
    hera3 = Heray("./img/hera.png", 800, 5, 180)
    hera4 = Heray("./img/hera2.png", 1000, -5, 180)
    hera5 = Herax("./img/hera3.png", 500, -5, 0)
    hera6 = Herax("./img/hera4.png", 200, 5, 0)
    hera7 = Herax("./img/hera3.png", 1000, -5)
    hera8 = Herax("./img/hera4.png", 700, 5)

    syabel1 = Syabely("./img/syabel2.png", 400, 5)
    syabel2 = Syabely("./img/syabel.png", 200, -5)
    syabel3 = Syabely("./img/syabel.png", 800, 5)
    syabel4 = Syabely("./img/syabel2.png", 1000, -5)
    syabel5 = Syabelx("./img/syabel3.png", 200, -5)
    syabel6 = Syabelx("./img/syabel4.png", 500, 5)
    syabel7 = Syabelx("./img/syabel3.png", 700, -5)
    syabel8 = Syabelx("./img/syabel4.png", 1000, 5)


    Soldiers = []
    hitpoint = HitPoint(1000, 560)
    hitpoint2 = HitPoint(200, 80)
    player = Player(collider, hitpoint2, 400, SCREEN.height/2 - 30)
    player2 = Player(collider, hitpoint, 800, SCREEN.height/2 - 30)
    castle = Castle(collider, player, 'Rect_Info')
    castle2 = Castle(collider, player2, 'Rect_Info_2')
    fire = Fire('Rect_Info')
    fire2 = Fire('Rect_Info_2')

    bg = pygame.image.load("./img/bg0.jpg")
    bg1 = pygame.image.load("./img/bg1.jpg")
    #スタート画面キャラ
    intro = pygame.image.load("./img/player_1.png").convert_alpha()
    intro = pygame.transform.scale(intro, (64, 64))
    intro_rect = intro.get_rect()
    draw_height = [75, 320, 580]
    fighter1 = Fighter("./img/firefighter01.png", 200, 500, 400, 380)
    fighter2 = Fighter("./img/firefighter02.png", 1000, 600, 400, 380)
    fighter3 = Fighter("./img/firefighter03.png", 600, 200, 280, 300, 180)
    mark1 = Img("./img/mark01.png", 1000, 300, 200, 200, 180)
    mark2 = Img("./img/mark01.png", 200, 500, 200, 200)
    koji1 = Img("./img/koji01.png", 1000, 500, 400, 350)
    koji2 = Img("./img/mark02.png", 200, 200, 200, 200, 180)

    boulimgs1 = []
    boulimgs2 = []
    boulimg = pygame.image.load('./img/boul.png').convert_alpha()
    boulimg2 = pygame.image.load('./img/boul2.png').convert_alpha()
    boulimg = pygame.transform.scale(boulimg,(450,250))
    boulimg2 = pygame.transform.scale(boulimg2,(450,250))
    #１枚の画像を回転させながら3枚格納
    for i in range(3):
        boulimg = pygame.transform.rotate(boulimg, 9 * i)
        boulimgs1.append(boulimg)
    for i in range(3):
        boulimg2 = pygame.transform.rotate(boulimg2, 9 * i)
        boulimgs2.append(boulimg2)

    index = 0
    color = [255, 255, 255]
    flag = 0
    idx = 1

    clock = pygame.time.Clock()

    #フラグ判定
    step1_start = False
    game_start = False
    game_play = False
    game_over = False
    game_clear = False
    dashi_start = False
    last_scean = True

    while True:
        screen.fill((0, 0, 0))
        clock.tick(60)  #フレームレート60fps

        if step1_start:
            time+= 1
            if time < 1800:
                group1.draw(screen)
                group1.update()
                pygame.display.update()
            elif 1800 <= time < 5400:
                screen.blit(bg, (100, 150))
                pygame.display.update()
            elif 5400 <= time < 7200:
                screen.blit(bg, (100, 150))
                group4.draw(screen)
                group4.update()
                pygame.display.update()
            else:
                time = 0
                step1_start = False
                game_start = True
                

        #説明画面
        if game_start:
            time += 1
            for i in draw_height:
                screen.blit(intro, (SCREEN.width/2 - 130, i - 15))
                draw_text(screen, "体力がなくなる前に", 40, SCREEN.width/2 -310, i)
                draw_text(screen, "の周りに土手を作り守れ(1分)", 40, SCREEN.width/2 + 210, i)
            pygame.display.update()
            Rect_Info = ((0, 0), (0, 0))
            Rect_Info_2 = ((0, 0), (0, 0))

            if time == 300:
                game_start = False
                game_play = True

        #実際のアニメーション画面
        if game_play:
            time += 1
            limit_time -= 1
            group.update()
            group.draw(screen)
            hitpoint.draw(screen)
            hitpoint2.draw(screen)
            draw_text(screen, f"制限時間:{int(limit_time/60)}", 40, 990, 600)

            if time % 360 == 0 and len(Soldiers) < 8:
                Soldiers.append(Soldier(random.randint(0, 1280), random.randint(0, 500), player, player2, castle, castle2))

            #画面更新(updateにdirty rectsを渡すとその部分だけ更新するので効率が良い)
            pygame.display.update()

            #城を出す
            check1 = detect_dote
            check2 = detect_dote2
            game_clear1 = game_clear2 = ""

            if check1 == "True":
                game_clear1 = castle.Move()
            if check2 == "True":
                game_clear2 = castle2.Move()
            if game_clear1 and game_clear2:
                game_play = False
                game_clear = True
                time = 0

            if hitpoint.hp <= 0 or hitpoint2.hp <= 0 or limit_time <= 0:
                pygame.time.wait(3)
                game_play = False
                game_over = True
                time = 0

        #クリア画面
        if game_clear:
            time += 1
            text_surface = font.render("Conguratulation", True, (color[0], color[1], color[2]))
            text_rect = text_surface.get_rect()
            text_rect.midtop = (SCREEN.width/2, SCREEN.height/2-50)
            screen.blit(text_surface, text_rect)
            draw_text(screen, "次の手順に進みましょう!!", 40, SCREEN.width/2, 75)
            draw_text(screen, "次の手順に進みましょう!!", 40, SCREEN.width/2, 580)
            pygame.display.update()
            
            #文字色の変更
            for i in range(len(color)):
                if i != idx:
                    if flag == 0:
                        color[i] -= 1
                    else:
                        color[i] += 1
            
            #色上下限確認
            if color[0] <= 0:
                flag = 1
            elif color[0] >= 255:
                flag = 0

                #インデックス変更
                if idx >= len(color):
                    idx = 1
                else:
                    idx += 1

            if time == 480:
                game_clear = False
                dashi_start = True
                time = 0
                
        if game_over:
            time += 1
            draw_text(screen, "早く土手を作りましょう!", 60, SCREEN.width/2, SCREEN.height/2)
            pygame.display.update()
            if time == 480:
                game_over = False
                dashi_start = True
                time = 0
        
        if dashi_start:
            time += 1
            if time < 12:
                index += 1
                draw_text(screen, "出汁を注ぎましょう!!", 40, SCREEN.width/2, 75)
                draw_text(screen, "出汁を注ぎましょう!!", 40, SCREEN.width/2, 580)
                if index >= len(boulimgs1):
                    index = 0
                boulimg = boulimgs1[index]
                boulimg2 = boulimgs2[index]
                clock.tick(3)
                screen.blit(boulimg, (800 , 150))
                screen.blit(boulimg2, (20 , 150))
                detect_dashi = False
                pygame.display.update()
            else:
                check = detect_dashi
                fire.update(screen)
                fire2.update(screen)
                group2.draw(screen)
                group2.update()
                clock.tick(10)
                pygame.display.update()
                if check == "True" or time > 800:
                    pygame.time.wait(30)
                    time = 0
                    dashi_start = False
                    last_scean = True
        
        if last_scean:
            time += 1
            if time < 1800:
                group3.draw(screen)
                group3.update()
                pygame.display.update()
            elif 1800 <= time < 5400:
                group3.draw(screen)
                group3.update()
                group6.draw(screen)
                group6.update()
                pygame.display.update()
            elif 5400 <= time < 9000:
                screen.blit(bg1, (50, 150))
                group7.update()
                group7.draw(screen)
                pygame.display.update()
            elif 9000 <= time < 9600:
                for i in draw_height:
                    draw_text(screen, "全ての工程が完了しました", 40, SCREEN.width/2, i)
                pygame.display.update()
            else:
                exit()
                
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


# class Hera(pygame.sprite.Sprite):
#     def __init__(self, filename, x, y, dx, angle, vege):
#         pygame.sprite.Sprite.__init__(self, self.containers)
#         self.image = pygame.image.load(filename).convert_alpha()
#         if angle !=0:
#             self.image = pygame.transform.rotate(self.image, angle)
#         self.image = pygame.transform.scale(self.image, (200, 200))
#         self.rect = self.image.get_rect()
#         self.rect.center = (x,y)
#         self.dx = dx
#         self.vege = vege
#         self.radius = 400
#         self.x_center = 1280/2
#         self.y_center = 720/2
#         self.count = 0
#         self.a = 3.14/360
#         self.deg = 0
#         self.rad = 0
#         self.angle = 0
       
#     def sin(self):
#         self.rect.centerx -= self.dx
#         self.rect.centery = int(50 * math.sin(math.radians(self.rect.centerx)*6)) + 300
#         #壁と衝突時の処理(跳ね返り)
#         if self.rect.left < 0 or self.rect.right > SCREEN.width:
#             self.dx = -self.dx
#         if self.rect.left == self.vege.rect.right or self.rect.right == self.vege.rect.left:
#             self.dx = -self.dx
#         if self.rect.colliderect(self.vege.rect) and self.dx > 0 or self.vege.rect.contains(self.rect):
#             self.rect.center = (random.randint(100,700),random.randint(100,500))
    
#     def maru(self):
#         self.angle +=1
#         self.count += self.a/3.14
#         self.rad += self.count
#         self.rect.centerx = int(self.radius * math.cos(self.rad))+self.x_center
#         self.rect.centery = int(self.radius * math.sin(self.rad))+self.y_center
#         if self.count >= 3.14/10:
#             self.count = 0

def check_font(font='Arial.ttf', size=10):
    # Return a PIL TrueType Font, downloading to CONFIG_DIR if necessary
    font = Path(font)
    font = font if font.exists() else (CONFIG_DIR / font.name)
    try:
        return ImageFont.truetype(str(font) if font.exists() else font.name, size)
    except Exception as e:  # download if missing
        url = "https://ultralytics.com/assets/" + font.name
        print(f'Downloading {url} to {font}...')
        torch.hub.download_url_to_file(url, str(font), progress=False)
        return ImageFont.truetype(str(font), size)

class Annotator:
    if RANK in (-1, 0):
        check_font()  # download TTF if necessary

    # YOLOv5 Annotator for train/val mosaics and jpgs and detect/hub inference annotations
    def __init__(self, im, line_width=None, font_size=None, font='Arial.ttf', pil=False, example='abc'):
        assert im.data.contiguous, 'Image not contiguous. Apply np.ascontiguousarray(im) to Annotator() input images.'
        self.pil = pil or not is_ascii(example) or is_chinese(example)
        if self.pil:  # use PIL
            self.im = im if isinstance(im, Image.Image) else Image.fromarray(im)
            self.draw = ImageDraw.Draw(self.im)
            self.font = check_font(font='Arial.Unicode.ttf' if is_chinese(example) else font,
                                   size=font_size or max(round(sum(self.im.size) / 2 * 0.035), 12))
        else:  # use cv2
            self.im = im
        self.lw = line_width or max(round(sum(im.shape) / 2 * 0.003), 2)  # line width
        self.count = 0

    def box_label(self, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        # Add one xyxy box to image with label
        if self.pil or not is_ascii(label):
            self.draw.rectangle(box, width=self.lw, outline=color)  # box
            if label:
                w, h = self.font.getsize(label)  # text width, height
                outside = box[1] - h >= 0  # label fits outside box
                self.draw.rectangle([box[0],
                                     box[1] - h if outside else box[1],
                                     box[0] + w + 1,
                                     box[1] + 1 if outside else box[1] + h + 1], fill=color)
                # self.draw.text((box[0], box[1]), label, fill=txt_color, font=self.font, anchor='ls')  # for PIL>8.0
                self.draw.text((box[0], box[1] - h if outside else box[1]), label, fill=txt_color, font=self.font)
        else:  # cv2
            global Rect_Info
            global Rect_Info_2
            p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
            cv2.rectangle(self.im, p1, p2, color, thickness=self.lw, lineType=cv2.LINE_AA)
            if "dote" in label:
                if p1[0] < 640:
                    Rect_Info = p1, p2
                else:
                    Rect_Info_2 = p1,p2
            if label:
                tf = max(self.lw - 1, 1)  # font thickness
                w, h = cv2.getTextSize(label, 0, fontScale=self.lw / 3, thickness=tf)[0]  # text width, height
                outside = p1[1] - h - 3 >= 0  # label fits outside box
                p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
                cv2.rectangle(self.im, p1, p2, color, -1, cv2.LINE_AA)  # filled
                cv2.putText(self.im, label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2), 0, self.lw / 3, txt_color,
                            thickness=tf, lineType=cv2.LINE_AA)

    def rectangle(self, xy, fill=None, outline=None, width=1):
        # Add rectangle to image (PIL-only)
        self.draw.rectangle(xy, fill, outline, width)

    def text(self, xy, text, txt_color=(255, 255, 255)):
        # Add text to image (PIL-only)
        w, h = self.font.getsize(text)  # text width, height
        self.draw.text((xy[0], xy[1] - h + 1), text, fill=txt_color, font=self.font)

    def result(self):
        # Return annotated image as array
        return np.asarray(self.im)

@torch.no_grad()
def run(weights=ROOT / 'yolov5s.pt',  # model.pt path(s)
        source=ROOT / 'data/images',  # file/dir/URL/glob, 0 for webcam
        imgsz=640,  # inference size (pixels)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        # project=ROOT / 'runs/detect',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        ):
    source = str(source)
    save_img = not nosave and not source.endswith('.txt')  # save inference images
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
    if is_url and is_file:
        source = check_file(source)  # download

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn)
    stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Half
    half &= pt and device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
    if pt:
        model.model.half() if half else model.model.float()

    # Dataloader
    if webcam:
        view_img = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt and not jit)
        bs = len(dataset)  # batch_size
        check = True
        global detect_dote
        global detect_dashi
        global detect_dote2
        detect_dote = "False"
        detect_dote2 = "False"
        detect_dashi = "False"
        # rs = RealsenseCamera()
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit)
        bs = 1  # batch_size
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    if pt and device.type != 'cpu':
        model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
    dt, seen = [0.0, 0.0, 0.0], 0

    for path, im, im0s, vid_cap, s in dataset:
        t1 = time_sync()
        im = torch.from_numpy(im).to(device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        # visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
        pred = model(im, augment=augment, visualize=visualize)
        t3 = time_sync()
        dt[1] += t3 - t2

        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        dt[2] += time_sync() - t3

        # Second-stage classifier (optional)
        # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            seen += 1
            if webcam:  # batch_size >= 1
                p, im0, frame = path[i], im0s[i].copy(), dataset.count
                s += f'{i}: '
            else:
                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            s += '%gx%g ' % im.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            imc = im0.copy() if save_crop else im0  # for save_crop
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    # #ラベル判別 
                    if names[int(c)] == "dashi":
                        detect_dashi = "True"
                        try:
                            end_time = time.time()
                            # print(end_time - start_time)
                            if(check):
                                thread1 = threading.Thread(target=ProjectM)
                                thread1.start()  
                                # thread1.join()
                                check = False
                        except NameError:
                            start_time = time.time()
                            print("ellipseがない")
                    else:
                        detect_dashi = "False"

                    if names[int(c)] == "dote":
                        if 'Rect_Info' in globals():
                            detect_dote = "True"
                        if 'Rect_Info_2' in globals():
                            detect_dote2 = "True"

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                        # with open(txt_path + '.txt', 'a') as f:
                        #     f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or save_crop or view_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))
                        # if save_crop:
                        #     save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

            # Print time (inference-only)
            # LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')

            # Stream results
            im0 = annotator.result()
            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'yolov5s.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default=ROOT / 'data/images', help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    # parser.add_argument('--project', default=ROOT / 'runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(FILE.stem, opt)
    return opt


def main(opt):
    check_requirements(exclude=('tensorboard', 'thop'))
    run(**vars(opt))


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)