import pygame
import sys
import cv2
from rearview_camera import rearview_camera
from pygame.locals import FULLSCREEN


CAMERA_SIZE = (240, 180)
CAMERA_MARGIN = 20
TEXT_COLOR = (0, 255, 0)
TEXT_X = 20
VALUE_X = 200
TEXT_Y = 20
TEXT_LINE_HEIGHT = 40


def draw_metric(screen, font, row, label, value):
    y = TEXT_Y + (TEXT_LINE_HEIGHT * row)
    label_text = font.render(label, True, TEXT_COLOR)
    value_text = font.render(value, True, TEXT_COLOR)
    screen.blit(label_text, [TEXT_X, y])
    screen.blit(value_text, [VALUE_X, y])


def main():
    '''
    ゲームの設定：
        画面の大きさ、タイトル、必要なファイルの用意など
    '''
    pygame.init()  # Pygameの初期化
    screen = pygame.display.set_mode((0, 0), FULLSCREEN)  # 現在の画面解像度でフルスクリーン表示
    pygame.display.set_caption('cycle computer AR')  # 画面上部に表示するタイトルを設定
    font1 = pygame.font.SysFont("sfns", 30)
    font1_bold = pygame.font.SysFont("sfcamera", 30, bold=True)
    speed = 20
    latitude = [30.0125,"N"]
    longitude = [141.0961, "E"]
    altitude  = 100
    camera = cv2.VideoCapture(0)
    '''
    ゲーム内の動き
    '''
    while True:
        screen.fill((0, 0, 0))  # 画面を塗りつぶし((R, G, B))
        draw_metric(screen, font1, 0, "SPEED", f"{speed}km/h")
        draw_metric(screen, font1, 1, "LATITUDE", f"{latitude[0]}˚ {latitude[1]}")
        draw_metric(screen, font1, 2, "LONGITUDE", f"{longitude[0]}˚ {longitude[1]}")
        draw_metric(screen, font1, 3, "ALTITUDE", f"{altitude}km/h")

        rearview_camera(camera, CAMERA_SIZE, CAMERA_MARGIN, pygame.surfarray, screen)

        pygame.display.update()  # 画面を更新
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 閉じるボタンが押されたら終了
                camera.release()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    camera.release()
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:
                    speed += 1
                elif event.key == pygame.K_DOWN:
                    speed -= 1
                    

                    


if __name__ == '__main__':
    main()
