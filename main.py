import pygame
import sys
import cv2
from pygame.locals import *


CAMERA_SIZE = (240, 180)
CAMERA_MARGIN = 20


def main():
    '''
    ゲームの設定：
        画面の大きさ、タイトル、必要なファイルの用意など
    '''
    pygame.init()  # Pygameの初期化
    screen = pygame.display.set_mode((0, 0), FULLSCREEN)  # 現在の画面解像度でフルスクリーン表示
    pygame.display.set_caption('cycle computer AR')  # 画面上部に表示するタイトルを設定
    font1 = pygame.font.SysFont("sfcamera", 30)
    font1_bold = pygame.font.SysFont("sfcamera", 30, bold=True)
    speed = 20
    ratitude = [30.0125,"N"]
    altitude = [141.0961, "E"]
    camera = cv2.VideoCapture(0)
    '''
    ゲーム内の動き
    '''
    while True:
        screen.fill((0, 0, 0))  # 画面を塗りつぶし((R, G, B))
        speed_text = font1.render(f"SPEED:   {speed}km/h", True, (0, 255, 0))
        screen.blit(speed_text, [20, 20])

        if camera.isOpened():
            ret, frame = camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, CAMERA_SIZE)
                camera_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                screen_width, screen_height = screen.get_size()
                camera_x = screen_width - CAMERA_SIZE[0] - CAMERA_MARGIN
                camera_y = screen_height - CAMERA_SIZE[1] - CAMERA_MARGIN
                screen.blit(camera_surface, (camera_x, camera_y))

        pygame.display.update()  # 画面を更新
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 閉じるボタンが押されたら終了
                camera.release()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    camera.release()
                    pygame.quit()
                    sys.exit()
                elif event.key == K_UP:
                    speed += 1
                elif event.key == K_DOWN:
                    speed -= 1
                    

                    


if __name__ == '__main__':
    main()
