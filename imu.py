import threading
import time
class IMU:
    def __init__(self, viewmodel):
        self.angle = -60
        self.increasing = True
        self._running = True
        self.viewmodel = viewmodel
        # Initialize the angle in viewmodel
        self.viewmodel.update_state('angle', self.angle)
        # Start the angle update thread
        self.thread = threading.Thread(target=self._update_angle)
        self.thread.daemon = True
        self.thread.start()

    def _update_angle(self):
        while self._running:
            if self.increasing:
                self.angle += 1
                if self.angle >= 60:
                    self.increasing = False
            else:
                self.angle -= 1
                if self.angle <= -60:
                    self.increasing = True
            # Update the angle in viewmodel
            self.viewmodel.update_state('angle', self.angle)
            time.sleep(0.1)

    def get_angle(self):
        return self.angle

    def cleanup(self):
        self._running = False
        self.thread.join()