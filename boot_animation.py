import sys

import cv2
import pygame


class BootAnimation:
    def __init__(self) -> None:
        self.video = cv2.VideoCapture("./animation/boot_animation.mp4")

    def play_boot_video(self, screen, clock, surfarray):
        if not self.video.isOpened():
            return 
        fps = self.video.get(cv2.CAP_PROP_FPS,)
        if fps <= 0:
            fps = 30
        screen_width, screen_height = screen.get_size()

        while True:
            ret, frame = self.video.read()

            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (screen_width, screen_height))
            surface = surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(surface, (0, 0))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.video.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.video.release()
                    pygame.quit()
                    sys.exit()
            clock.tick(fps)
        self.video.release()
                

        
        
        
            
