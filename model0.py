import cv2
import random
import numpy as np

class CameraModel:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.last_frame = None
        self.current_frame = None
        self.images = [None, None, None, None]  # Store all four images
        self.current_image_num = 1

    def store_current_image(self):
        self.images[self.current_image_num - 1] = self.current_frame.copy()

    def get_stored_images(self):
        return self.images

    def reset_images(self):
        self.images = [None, None, None, None]
        self.current_image_num = 1

    def read_camera(self):
        ret, frame = self.camera.read()
        if ret:
            self.current_frame = frame
            return True
        return False

    def has_frame_changed(self):
        if self.last_frame is None:
            self.last_frame = self.current_frame.copy()
            return False
        
        if self.current_frame is None:
            return False
        
        diff = cv2.absdiff(self.last_frame, self.current_frame)
        change = cv2.sumElems(diff)[0]
        threshold = 1000000  # Adjust this value based on your needs
        
        
        if change > threshold:
            self.last_frame = self.current_frame.copy()
            return True
        return False

    def validate_frame(self):
        # Simulating validation that passes 1 out of 5 times
        return random.randint(1, 20) == 1

    def get_current_frame(self):
        return self.current_frame

    def __del__(self):
        self.camera.release()