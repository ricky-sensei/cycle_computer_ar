import cv2
import pygame

class Rear_Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.CAMERA_SIZE = (240, 180)
        self.CAMERA_MARGIN = 20
        self.CAMERA_CORNER_RADIUS = 18
        self.ERROR_COLOR = (255, 0, 0)
        self.ERROR_BORDER_WIDTH = 3
        self.ERROR_FONT_SIZE = 20
        self.ERROR_MIN_FONT_SIZE = 12
        self.ERROR_TEXT_PADDING = 12

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

    def _camera_rect(self, screen):
        screen_width, screen_height = screen.get_size()
        return pygame.Rect(
            screen_width - self.CAMERA_SIZE[0] - self.CAMERA_MARGIN,
            screen_height - self.CAMERA_SIZE[1] - self.CAMERA_MARGIN,
            self.CAMERA_SIZE[0],
            self.CAMERA_SIZE[1],
        )

    def _draw_error(self, screen, error_text):
        camera_rect = self._camera_rect(screen)
        lines = error_text.splitlines()
        max_text_width = camera_rect.width - (self.ERROR_TEXT_PADDING * 2)
        max_text_height = camera_rect.height - (self.ERROR_TEXT_PADDING * 2)

        for font_size in range(self.ERROR_FONT_SIZE, self.ERROR_MIN_FONT_SIZE - 1, -1):
            font = pygame.font.SysFont("sfcamera", fonwet_size, bold=True)
            rendered_lines = [font.render(line, True, self.ERROR_COLOR) for line in lines]
            line_height = font.get_linesize()
            total_height = line_height * len(rendered_lines)
            widest_line = max(line.get_width() for line in rendered_lines)
            if widest_line <= max_text_width and total_height <= max_text_height:
                break

        y = camera_rect.centery - total_height // 2

        pygame.draw.rect(
            screen,
            self.ERROR_COLOR,
            camera_rect,
            width=self.ERROR_BORDER_WIDTH,
            border_radius=self.CAMERA_CORNER_RADIUS,
        )

        for rendered_line in rendered_lines:
            line_rect = rendered_line.get_rect(centerx=camera_rect.centerx, y=y)
            screen.blit(rendered_line, line_rect)
            y += line_height

    def rear_camera(self, surfarray, screen, frame_count):
        # エラー表示チェック用
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            camera_rect = self._camera_rect(screen)
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, self.CAMERA_SIZE)
                camera_surface = surfarray.make_surface(frame.swapaxes(0, 1))
                camera_surface = self._round_corners(camera_surface)
                alpha = 255 / 30 * frame_count if frame_count < 30 else 255
                camera_surface.set_alpha(alpha)
                screen.blit(camera_surface, camera_rect)
            else:
                error_text = "video loading error"
                self._draw_error(screen, error_text)

        else:
            error_text = "camera connection error\nmake sure camera is connected."
            self._draw_error(screen, error_text)
            
