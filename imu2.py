import threading
import time
import keyboard  # You'll need to install this: pip install keyboard

class IMU2:
    def __init__(self, port):
        self.angle = 0
        self.rotation_angle = 0
        self.is_connected = False
        self.battery_level  = 100
        
    def set_tilt(self, a):
        self.angle = a

    def set_rotation(self, a):
        self.rotation_angle = a

    def activeside(self):
        if -50 < self.rotation_angle < 50:
            if -20 < self.rotation_angle < 20: return 'ap'
            return 'ob'
        return None