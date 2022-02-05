import pygame
from pygame.locals import *
import sys

#画面サイズ
SCREEN = Rect(0, 0, 800, 600)

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    images = []
    for i in range(27):
        number_str = str(i)
        if len(number_str) == 1:
            number_str = number_str
        images.append(pygame.image.load('../img/btleffect_' + number_str + '.png'))
    image = images[0]
    index = 0

    while True:
        screen.fill((0, 0, 0))
        screen.blit(image, (0, 0))

        image = images[index]
        if index < len(images) - 1 :
            index += 1

        pygame.display.update()
        clock.tick(10)        

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