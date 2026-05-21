import cv2

class Rear_Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.CAMERA_SIZE = (240, 180)
        self.CAMERA_MARGIN = 20
    def rear_camera(self, surfarray, screen):
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, self.CAMERA_SIZE)
                camera_surface = surfarray.make_surface(frame.swapaxes(0, 1))
                screen_width, screen_height = screen.get_size()
                camera_x = screen_width - self.CAMERA_SIZE[0] - self.CAMERA_MARGIN
                camera_y = screen_height - self.CAMERA_SIZE[1] - self.CAMERA_MARGIN
                screen.blit(camera_surface, (camera_x, camera_y))



