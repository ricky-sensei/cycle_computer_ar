import pygame
import sys
import cv2
from mock_gps import MockGPS
from boot_animation import BootAnimation
from rear_camera import Rear_Camera
from pygame.locals import FULLSCREEN


CAMERA_SIZE = (240, 180)
CAMERA_MARGIN = 20

TEXT_X = 20
VALUE_X = 200
TEXT_Y = 20
TEXT_LINE_HEIGHT = 40

# color
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

rear_camera= Rear_Camera()
boot_animation = BootAnimation()

def draw_metric(screen, font, row, label, value):
    y = TEXT_Y + (TEXT_LINE_HEIGHT * row)
    label_text = font.render(label, True, GREEN)
    value_text = font.render(value, True, GREEN)
    screen.blit(label_text, [TEXT_X, y])
    screen.blit(value_text, [VALUE_X, y])


def main():
    '''
    ゲームの設定：
        画面の大きさ、タイトル、必要なファイルの用意など
    '''
    pygame.init()  # Pygameの初期化
    screen = pygame.display.set_mode((0, 0), FULLSCREEN)  # 現在の画面解像度でフルスクリーン表示
    font1 = pygame.font.SysFont("sfns", 30)
    font1_bold = pygame.font.SysFont("sfcamera", 30, bold=True)
    gps = MockGPS()
    surfarray = pygame.surfarray
    boot_animation.play_boot_video(screen, pygame.time.Clock(), surfarray)


    '''
    ゲーム内の動き
    '''
    while True:
        gps_data = gps.read()

        screen.fill(BLACK)  # 画面を塗りつぶし((R, G, B))
        draw_metric(screen, font1, 0, "GPS", "FIX" if gps_data["fix"] else "SEARCHING")
        draw_metric(screen, font1, 1, "SPEED", f"{gps_data['speed_kmh']:.1f}km/h")
        draw_metric(screen, font1, 2, "LATITUDE", f"{abs(gps_data['lat']):.6f}deg {gps_data['lat_dir']}")
        draw_metric(screen, font1, 3, "LONGITUDE", f"{abs(gps_data['lon']):.6f}deg {gps_data['lon_dir']}")
        draw_metric(screen, font1, 4, "ALTITUDE", f"{gps_data['altitude_m']:.1f}m")
        draw_metric(screen, font1, 5, "HEADING", f"{gps_data['heading_deg']:.0f}deg")
        draw_metric(screen, font1, 6, "SATELLITES", str(gps_data["satellites"]))
        rear_camera.rear_camera(surfarray, screen)

        pygame.display.update()  # 画面を更新
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 閉じるボタンが押されたら終了
                rear_camera.camera.release()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    rear_camera.camera.release()
                    pygame.quit()
                    sys.exit()
                    
if __name__ == '__main__':
    main()
