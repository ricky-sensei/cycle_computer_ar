import pygame
import sys
from pygame.locals import *

SCREEN_SIZE = (600, 500)
def main():
    '''
    ゲームの設定：
        画面の大きさ、タイトル、必要なファイルの用意など
    '''
    pygame.init()  # Pygameの初期化
    screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN)  # 画面の大きさ（x方向, ｙ方向）
    pygame.display.set_caption('cycle computer AR')  # 画面上部に表示するタイトルを設定
    font1 = pygame.font.SysFont("sfcamera", 30)
    font1_bold = pygame.font.SysFont("sfcamera", 30, bold=True)
    speed = 20
    '''
    ゲーム内の動き
    '''
    while True:
        screen.fill((0, 0, 0))  # 画面を塗りつぶし((R, G, B))
        speed_text = font1.render(f"SPEED:   {speed}km/h", True, (0, 255, 0))
        screen.blit(speed_text, [20, 20])
        pygame.display.update()  # 画面を更新
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 閉じるボタンが押されたら終了
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                elif event.key == K_UP:
                    speed += 1
                elif event.key == K_DOWN:
                    speed -= 1
                    

                    


if __name__ == '__main__':
    main()
