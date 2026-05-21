import cv2
def rearview_camera(camera, CAMERA_SIZE, CAMERA_MARGIN, surfarray, screen):
    if camera.isOpened():
        ret, frame = camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, CAMERA_SIZE)
            camera_surface = surfarray.make_surface(frame.swapaxes(0, 1))
            screen_width, screen_height = screen.get_size()
            camera_x = screen_width - CAMERA_SIZE[0] - CAMERA_MARGIN
            camera_y = screen_height - CAMERA_SIZE[1] - CAMERA_MARGIN
            screen.blit(camera_surface, (camera_x, camera_y))



