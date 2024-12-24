import threading
import time
from typing import Optional, Union
import numpy as np
import cv2
from ab import AnalyzeBox
from fg import FrameGrabber

class ImageProcessingController:
    def __init__(self):
        self.frame_grabber = FrameGrabber()
        self.analyze_box = AnalyzeBox()
        
        self.is_running: bool = False
        self.process_thread: Optional[threading.Thread] = None
        
        self.current_image: Optional[np.ndarray] = None
        self.previous_image: Optional[np.ndarray] = None
        self.stitched_result: Optional[np.ndarray] = None
        
        self._check_frequency: float = 30.0
        self._lock = threading.Lock()

    def connect_camera(self, device_name: str) -> Union[bool, str]:
        """
        Connect to the specified camera device.
        """
        result = self.frame_grabber.initiateVideo(device_name)
        if isinstance(result, str):
            return result
        return True

    def start_processing(self, frequency: float = 30.0) -> Union[bool, str]:
        """
        Start the image processing loop.
        """
        # Start the frame grabber
        result = self.frame_grabber.startVideo(frequency)
        if isinstance(result, str):
            return result
        
        self._check_frequency = frequency
        self.is_running = True
        self.process_thread = threading.Thread(target=self._process_loop)
        self.process_thread.start()
        return True

    def stop_processing(self) -> Union[bool, str]:
        """
        Stop the image processing loop.
        """
        self.is_running = False
        if self.process_thread:
            self.process_thread.join()
            self.process_thread = None
        
        # Stop the frame grabber
        result = self.frame_grabber.stopVideo()
        if isinstance(result, str):
            return result
        return True

    def _process_loop(self):
        """
        Main processing loop that checks for new frames and processes them.
        """
        while self.is_running:
            # Fetch a new frame if available
            frame = self.frame_grabber.fetchFrame()
            
            if frame is not None:
                # Crop the frame
                cropped_frame = self.analyze_box.crop_center(frame)
                
                with self._lock:
                    if self.current_image is None:
                        # This is the first image of a pair
                        self.current_image = cropped_frame
                    else:
                        # This is the second image, time to stitch
                        self.previous_image = self.current_image
                        self.current_image = cropped_frame
                        
                        # Start stitching in a separate thread
                        self.analyze_box.stitch(self.previous_image, self.current_image)
                        
                        # Reset for the next pair
                        self.current_image = None
                        self.previous_image = None
            
            # Check if stitching is complete
            if not self.analyze_box.is_stitching:
                result = self.analyze_box.get_result()
                if result is not None:
                    with self._lock:
                        self.stitched_result = result
            
            # Sleep to maintain the desired frequency
            time.sleep(1 / self._check_frequency)

    def get_current_image(self) -> Optional[np.ndarray]:
        """
        Get the current cropped image.
        """
        with self._lock:
            return self.current_image

    def get_stitched_result(self) -> Optional[np.ndarray]:
        """
        Get the stitched result image.
        """
        with self._lock:
            return self.stitched_result

    def get_stitch_progress(self) -> int:
        """
        Get the current progress of the stitching operation.
        """
        return self.analyze_box.stitch_progress

    def is_stitching(self) -> bool:
        """
        Check if a stitching operation is currently in progress.
        """
        return self.analyze_box.is_stitching

    def disconnect_camera(self) -> Union[bool, str]:
        """
        Disconnect from the camera and clean up resources.
        """
        # First, stop processing if it's running
        if self.is_running:
            result = self.stop_processing()
            if isinstance(result, str):
                return result
        
        # Close the video connection
        return self.frame_grabber.closeVideo()

controller = ImageProcessingController()

# Connect to a camera
result = controller.connect_camera("OBS Virtual Camera")
if isinstance(result, str):
    print(f"Error: {result}")
    exit()

# Start processing
result = controller.start_processing(30)  # 30 Hz
if isinstance(result, str):
    print(f"Error: {result}")
    controller.disconnect_camera()
    exit()

try:
    while True:
        # Check stitching progress
        if controller.is_stitching():
            print(f"Stitching progress: {controller.get_stitch_progress()}%")
        
        # Get stitched result if available
        stitched_result = controller.get_stitched_result()
        if stitched_result is not None:
            # Process or display the stitched result
            cv2.imshow("Stitched Result", stitched_result)
        
        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Clean up
    controller.disconnect_camera()
    cv2.destroyAllWindows()