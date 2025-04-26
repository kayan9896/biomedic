import threading
import time
import keyboard  # You'll need to install this: pip install keyboard

class IMU2:
    def __init__(self, controller, port):
        self.angle = 0
        self.rotation_angle = 0
        self.controller = controller
        self.is_connected = False
        self.battery_level  = 100
        
    def set_tilt(self, a):
        self.angle = a
        self.controller.viewmodel.update_state('angle', self.angle)

    def set_rotation(self, a):
        self.rotation_angle = a
        self.controller.viewmodel.update_state('rotation_angle', self.rotation_angle)