import threading
import time
import logging
import math

class IMU_sensor:
    def __init__(self, port, handler, panel, imu_simulation = False):
        self.tilt_angle = 0
        self.rotation_angle = 0
        self.is_connected = False
        self.battery_level = 100
        self.handler = handler
        self.panel = panel
        self.imu_simulation = imu_simulation

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def start(self, frequency: float = 30.0):
        try:
            self.check_thread = threading.Thread(
                target=self.imu_loop,
                args=(frequency,),
                #daemon=True
            )
            self.check_thread.start()
            
            self.logger.info(f"Started imu checking at {frequency} Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting imu: {str(e)}")
            return f"Error starting imu: {str(e)}"

    def imu_loop(self, frequency: float):
        """Main loop for checking video frames"""
        period = 1.0 / frequency
        
        while True:
            self.is_connected = self.panel.is_connected
            self.battery_level = self.panel.battery_level
            noise = self.panel.noise * math.sin(time.time()**2)
            self.set_tilt(self.panel.tilt_angle + noise)
            self.set_rotation(self.panel.rotation_angle + noise)
            time.sleep(period)

    def check_tilt_sensor(self):
        self.start()        
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
    