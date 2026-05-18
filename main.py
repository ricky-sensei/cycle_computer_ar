import pygame
import sys


def main():
    '''
    ゲームの設定：
        画面の大きさ、タイトル、必要なファイルの用意など
    '''
    pygame.init()  # Pygameの初期化
    screen = pygame.display.set_mode((400, 300))  # 画面の大きさ（x方向, ｙ方向）
    pygame.display.set_caption('cycle computer AR')  # 画面上部に表示するタイトルを設定
    font1 = pygame.font.SysFont("")
    '''
    ゲーム内の動き
    '''
    while True:
        screen.fill((0, 0, 0))  # 画面を塗りつぶし((R, G, B))
        pygame.display.update()  # 画面を更新
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 閉じるボタンが押されたら終了
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    main()
