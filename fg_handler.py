import cv2
import numpy as np
from typing import Dict, Optional, Union
from fg import FrameGrabber
from datetime import datetime

class FrameGrabber_handler:
    def __init__(self, calib, panel, fg_simulation, logger = None, controller = None):
        self._is_new_frame_available: bool = False
        self._last_fetch_time: Optional[datetime] = None
        self.last_frame = None
        self.fg_simulation = fg_simulation
        self.calib = calib

        self.sensor = panel if fg_simulation else FrameGrabber(panel, calib.get("fg_handler_config", None), fg_simulation, logger)
        self.sensor.fg_handler = self
        self.logger = logger
        self.controller = controller

    def update_select(self, calib):
        self.calib = calib
        self.sensor.calib = calib.get("fg_handler_config", None)

    # Modified fetchFrame to update frame availability status
    def fetchFrame(self) -> Optional[np.ndarray]:
        """Get the most recent frame"""

        self._is_new_frame_available = False  # Reset flag when frame is fetched
        self._last_fetch_time = datetime.now()
        if self.last_frame is not None:
            self.controller.run2(self.mask(self.last_frame.copy()) )
                             
    def connect(self, device) -> Union[bool, str]:
        return self.sensor.connect(device)
 

    def get_fg_states(self):
        is_connected = getattr(self.sensor, 'fg_is_connected', False)
        is_running = getattr(self.sensor, 'fg_is_running', False)
        return {'video_on': is_connected and is_running}
    
    def mask(self, frame):
        m = cv2.imread(self.calib.get("fg_handler_config").get("image_mask_path"))
        m = cv2.resize(m, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        w, h = m.shape[:2]
        frame[:h, :w] = m
        return frame



                