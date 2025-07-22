import threading
import time

class IMU_sensor:
    def __init__(self, port, handler):
        self.tilt_angle = 0
        self.rotation_angle = 0
        self.is_connected = False
        self.battery_level = 100
        self.handler = handler

    def check_tilt_sensor(self):        
        if not self.is_connected:
            message = "Tilt sensor disconnected. Please check the connection."
        elif self.battery_level < 30:
            message = "Tilt sensor connected but battery is low. Consider replacing batteries soon."
        else:
            message = "Tilt sensor connected successfully."
        return {
            "connected": self.is_connected,
            "battery_low": self.battery_level < 30,
            "message": message
        }
    
    def set_tilt(self, a):
        self.tilt_angle = a
        self.handler.set_tilt(a)

    def set_rotation(self, a):
        self.rotation_angle = a
        self.handler.set_rotation(a)
    