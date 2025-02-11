import threading
import time
import keyboard  # You'll need to install this: pip install keyboard

class IMU:
    def __init__(self, viewmodel):
        self.angle = 0
        self.viewmodel = viewmodel
        self._auto_mode = False  # Start in manual mode
        self._running = True
        self.increasing = True
        
        # Initialize the angle in viewmodel
        self.viewmodel.update_state('angle', self.angle)
        
        # Start the angle update thread
        self.thread = threading.Thread(target=self._update_angle)
        self.thread.daemon = True
        self.thread.start()
        
        # Start keyboard listener
        self._setup_keyboard_controls()

    def _update_angle(self):
        while self._running:
            if self._auto_mode:
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

    def _setup_keyboard_controls(self):
        try:
            keyboard.on_press_key('z', lambda _: self._adjust_angle(-5))
            keyboard.on_press_key('x', lambda _: self._adjust_angle(5))
            keyboard.on_press_key('a', lambda _: self._toggle_auto_mode())
            print("Keyboard controls enabled:")
            print("  Press 'z' to decrease angle by 5")
            print("  Press 'x' to increase angle by 5")
            print("  Press 'a' to toggle auto mode")
        except:
            print("Failed to setup keyboard controls. Make sure you have admin/root permissions.")

    def _adjust_angle(self, change):
        if not self._auto_mode:
            new_angle = min(max(self.angle + change, -60), 60)
            self.angle = new_angle
            self.viewmodel.update_state('angle', self.angle)
            print(f"Current angle: {self.angle}")

    def _toggle_auto_mode(self):
        self._auto_mode = not self._auto_mode
        print(f"Auto mode: {'ON' if self._auto_mode else 'OFF'}")

    def get_angle(self):
        return self.angle

    def cleanup(self):
        self._running = False
        self.thread.join()
        # Clean up keyboard listeners
        try:
            keyboard.unhook_all()
        except:
            pass