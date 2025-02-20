import cv2
import logging
import time
import threading
import numpy as np
from typing import Dict, Optional, Union
from pygrabber.dshow_graph import FilterGraph
from datetime import datetime
import pythoncom

class FrameGrabber:
    def __init__(self):
        self.device_name: str = ""
        self.device_index: int = -1
        self.capture = None
        self.is_connected: bool = False
        
        self._check_frequency: float = 30.0
        self._is_initialized: bool = False
        self._is_new_frame_available: bool = False
        self._last_capture_time: Optional[datetime] = None
        self._last_fetch_time: Optional[datetime] = None
        
        self.is_running: bool = False
        self.check_thread: Optional[threading.Thread] = None
        self.last_frame = None
        self.frame_lock = threading.Lock()
        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_available_devices(self) -> Dict[str, int]:
        """
        Get available video devices using pygrabber
        Returns a dictionary with device names as keys and their indices as values
        """
        try:
            pythoncom.CoInitialize()
            # Create FilterGraph instance
            graph = FilterGraph()
            # Get the list of available video input devices
            devices = graph.get_input_devices()
            # Create dictionary with device names and their indices
            available_devices = {name: idx for idx, name in enumerate(devices)}
            
            return available_devices
            
        except Exception as e:
            self.logger.error(f"Error getting available devices: {str(e)}")
            return {}

    def initiateVideo(self, device_name: str) -> Union[bool, str]:
        """
        Initiate video capture for the specified device
        
        Args:
            device_name (str): Name of the video device to connect to
            
        Returns:
            Union[bool, str]: True if connection successful, error message if failed
        """
        try:
            # Get available devices
            available_devices = self.get_available_devices()
            
            if not available_devices:
                return "No video devices found"
            
            # Log available devices
            self.logger.info("Available devices:")
            for name, idx in available_devices.items():
                self.logger.info(f"  - {name} (index: {idx})")
            
            # Check if the requested device exists
            if device_name not in available_devices:
                return f"Device '{device_name}' not found. Available devices: {list(available_devices.keys())}"
            
            # Store device information
            self.device_name = device_name
            self.device_index = available_devices[device_name]
            
            # Initialize video capture
            self.capture = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)
            
            if not self.capture.isOpened():
                return f"Failed to open device '{device_name}'"
            

            self._is_initialized = True
            self.is_connected = True
            self.logger.info(f"Successfully connected to {device_name}")
            
            return True
            
        except Exception as e:
            self._is_initialized = False
            self.is_connected = False
            self.logger.error(f"Error initiating video: {str(e)}")
            return f"Error initiating video: {str(e)}"


    def compare_frames(self, frame1, frame2, threshold=30) -> bool:
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
    def check_video_loop(self, frequency: float):
        """Main loop for checking video frames"""
        period = 1.0 / frequency
        
        while self.is_running:
            loop_start = time.time()
            
            if self.capture is None or not self.capture.isOpened():
                self.logger.error("Video capture is not available")
                break
                
            ret, current_frame = self.capture.read()
            
            if not ret:
                self.logger.error("Failed to read frame")
                continue
                
            with self.frame_lock:
                if self.last_frame is None:
                    self.last_frame = current_frame
                    continue
                if self.compare_frames(current_frame, self.last_frame):
                    self.last_frame = current_frame.copy()
                    self._last_capture_time = datetime.now()
                    self._is_new_frame_available = True
                    self.logger.debug("Frame updated")
            
            elapsed = time.time() - loop_start
            sleep_time = period - elapsed
            
            if sleep_time > 0:
                time.sleep(sleep_time)

    # Modified fetchFrame to update frame availability status
    def fetchFrame(self) -> Optional[np.ndarray]:
        """Get the most recent frame"""
        with self.frame_lock:
            self._is_new_frame_available = False  # Reset flag when frame is fetched
            self._last_fetch_time = datetime.now()
            return self.last_frame.copy() if self.last_frame is not None else None

    def startVideo(self, frequency: float = 30.0) -> Union[bool, str]:
        """
        Start checking video frames at the specified frequency
        
        Args:
            frequency: How many times per second to check for new frames
            
        Returns:
            Union[bool, str]: True if started successfully, error message if failed
        """
        try:
            if not self.is_connected:
                return "Video is not initiated. Call initiateVideo first."
                
            if self.is_running:
                return "Video checking is already running"
                
            self.is_running = True
            self.check_thread = threading.Thread(
                target=self.check_video_loop,
                args=(frequency,),
                #daemon=True
            )
            self.check_thread.start()
            
            self.logger.info(f"Started video checking at {frequency} Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting video: {str(e)}")
            return f"Error starting video: {str(e)}"

    def stopVideo(self) -> Union[bool, str]:
        """
        Stop checking video frames
        
        Returns:
            Union[bool, str]: True if stopped successfully, error message if failed
        """
        try:
            if not self.is_running:
                return "Video checking is not running"
                
            self.is_running = False
            
            if self.check_thread is not None:
                self.check_thread.join(timeout=1.0)
                self.check_thread = None
                
            with self.frame_lock:
                self.last_frame = None
                
            self.logger.info("Stopped video checking")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping video: {str(e)}")
            return f"Error stopping video: {str(e)}"


    def closeVideo(self) -> Union[bool, str]:
        """
        Close connection to the video device and clean up resources
        
        Returns:
            Union[bool, str]: True if closed successfully, error message if failed
        """
        try:
            # First stop the video checking if it's running
            if self.is_running:
                result = self.stopVideo()
                if isinstance(result, str):
                    return result

            # Release the capture object
            if self.capture is not None:
                self.capture.release()
                self.capture = None
                
            # Reset all variables
            self.is_connected = False
            
            with self.frame_lock:
                self.last_frame = None
                
            self.logger.info(f"Closed connection to {self.device_name}")
            
            self._is_initialized = False
            self.is_connected = False
            self._is_new_frame_available = False
            self._last_capture_time = None
            self._last_fetch_time = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing video: {str(e)}")
            return f"Error closing video: {str(e)}"

    def restartVideo(self) -> Union[bool, str]:
        """
        Close and reinitiate connection to the video device
        
        Returns:
            Union[bool, str]: True if restarted successfully, error message if failed
        """
        try:
            if not self.device_name:
                return "No device name stored. Cannot restart."
                
            # Store current frequency if video is running
            was_running = self.is_running
            frequency = None
            if was_running:
                # Estimate the actual frequency from the period between frames
                if hasattr(self, 'check_video_loop'):
                    frequency = 30.0  # default fallback
            
            # Close current connection
            result = self.closeVideo()
            if isinstance(result, str):
                return f"Error closing video during restart: {result}"
                
            # Reinitiate video
            result = self.initiateVideo(self.device_name)
            if isinstance(result, str):
                return f"Error reinitiating video: {result}"
                
            # Restart video checking if it was running before
            if was_running and frequency is not None:
                result = self.startVideo(frequency)
                if isinstance(result, str):
                    return f"Error restarting video checking: {result}"
                    
            self.logger.info(f"Successfully restarted video for {self.device_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restarting video: {str(e)}")
            return f"Error restarting video: {str(e)}"

if __name__=="__main__":
    frame_grabber = FrameGrabber()

    # Initialize video
    result = frame_grabber.initiateVideo("QP0203 PCI, Analog 01 Capture")
    if isinstance(result, str):
        print(f"Error: {result}")
        exit(1)

    # Start video checking with specific frequency
    frame_grabber._check_frequency = 60.0  # Change frequency to 60 Hz
    result = frame_grabber.startVideo(frame_grabber._check_frequency)

    try:
        while True:
            # Check status
            if not frame_grabber.is_connected:
                print("Video device dis_connected!")
                break

            if frame_grabber._is_new_frame_available:
                frame = frame_grabber.fetchFrame()
                if frame is not None:
                    print(f"New frame captured at: {frame_grabber._last_capture_time}")
                    cv2.imshow('Frame', frame)
                    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(1/frame_grabber._check_frequency)

    finally:
        frame_grabber.closeVideo()
        cv2.destroyAllWindows()

                