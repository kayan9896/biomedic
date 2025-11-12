import cv2
import numpy as np
from typing import Dict, Optional, Union
from .fg import FrameGrabber
from datetime import datetime

class FrameGrabber_handler:
    def __init__(self, calib, panel, fg_simulation, logger = None):
        self._is_new_frame_available: bool = False
        self._last_fetch_time: Optional[datetime] = None
        self.last_frame = None
        self.fg_simulation = fg_simulation

        self.sensor = panel if fg_simulation else FrameGrabber(panel, calib["FrameGrabber"], fg_simulation, logger)
        self.sensor.fg_handler = self
        self.logger = logger

    def compare_frames(self, frame1, frame2, threshold=10) -> bool:
        """
        Compare two frames and determine if they are different enough
        
        Args:
            frame1: First frame
            frame2: Second frame
            threshold: Minimum difference threshold (0-255)
            
        Returns:
            bool: True if frames are different enough, False otherwise
        """
        if frame1 is None or frame2 is None:
            return True
            
        # Convert frames to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Calculate mean difference
        mean_diff = np.mean(diff)
        
        return mean_diff > threshold


    # Modified check_video_loop to update new properties
    def handdle_frame(self, current_frame):
        if self.last_frame is None:
            self.last_frame = current_frame
            return
        if self.compare_frames(current_frame, self.last_frame):
            self.last_frame = current_frame.copy()
            self._last_capture_time = datetime.now()
            self._is_new_frame_available = True
            self.logger.debug("Frame updated")

    # Modified fetchFrame to update frame availability status
    def fetchFrame(self) -> Optional[np.ndarray]:
        """Get the most recent frame"""

        self._is_new_frame_available = False  # Reset flag when frame is fetched
        self._last_fetch_time = datetime.now()
        return self.last_frame.copy() if self.last_frame is not None else None

    def connect(self, device) -> Union[bool, str]:
        return self.sensor.connect(device)
 

    def get_fg_states(self):
        is_connected = getattr(self.sensor, 'fg_is_connected', False)
        is_running = getattr(self.sensor, 'fg_is_running', False)
        return {'video_on': is_connected and is_running}



                