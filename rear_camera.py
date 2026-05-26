import cv2
import pygame

class Rear_Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.CAMERA_SIZE = (240, 180)
        self.CAMERA_MARGIN = 20
        self.CAMERA_CORNER_RADIUS = 18

    def _round_corners(self, camera_surface):
        rounded_surface = pygame.Surface(self.CAMERA_SIZE, pygame.SRCALPHA)
        rounded_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(
            rounded_surface,
            (255, 255, 255, 255),
            rounded_surface.get_rect(),
            border_radius=self.CAMERA_CORNER_RADIUS,
        )
        rounded_surface.blit(
            camera_surface.convert_alpha(),
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MIN,
        )
        return rounded_surface

    def rear_camera(self, surfarray, screen):
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            screen_width, screen_height = screen.get_size()
            camera_x = screen_width - self.CAMERA_SIZE[0] - self.CAMERA_MARGIN
            camera_y = screen_height - self.CAMERA_SIZE[1] - self.CAMERA_MARGIN
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, self.CAMERA_SIZE)
                camera_surface = surfarray.make_surface(frame.swapaxes(0, 1))
                camera_surface = self._round_corners(camera_surface)
                screen.blit(camera_surface, (camera_x, camera_y))
            else:
                error_text = "video loading error"

        else:
            error_text = "camera connection error ¥n make sure camera is connected."
            


