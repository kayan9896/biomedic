import threading
import time
from typing import Optional
import numpy as np
import cv2
from ab import AnalyzeBox
from fg import FrameGrabber

class ImageProcessingController:
    def __init__(self, frame_grabber: 'FrameGrabber', analyze_box: 'AnalyzeBox'):
        self.frame_grabber = frame_grabber
        self.analyze_box = analyze_box
        
        self.is_running = False
        self.process_thread = None
        
        # Model storage
        self.first_cropped_image = None
        self.second_cropped_image = None
        self.stitched_result = None
        
        self.check_interval = 0.1  # Check for new frames every 100ms
        
        self.logger = frame_grabber.logger  # Reuse the logger from frame_grabber

    def start_processing(self):
        """Start the frame processing loop in a separate thread."""
        if self.is_running:
            self.logger.warning("Processing is already running")
            return
        
        self.is_running = True
        self.process_thread = threading.Thread(target=self._process_loop)
        self.process_thread.start()
        self.logger.info("Started image processing")

    def stop_processing(self):
        """Stop the frame processing loop."""
        if not self.is_running:
            self.logger.warning("Processing is not running")
            return
        
        self.is_running = False
        if self.process_thread:
            self.process_thread.join()
            self.process_thread = None
        self.logger.info("Stopped image processing")

    def _process_loop(self):
        """Main processing loop that checks for new frames and processes them."""
        while self.is_running:
            if self.frame_grabber._is_new_frame_available:
                # Fetch the new frame
                frame = self.frame_grabber.fetchFrame()
                if frame is not None:
                    # Crop the frame
                    cropped_frame = self.analyze_box.crop_center(frame)
                    
                    # Check if we already have a first image
                    if self.first_cropped_image is None:
                        # This is the first image
                        self.first_cropped_image = cropped_frame
                        self.logger.info("Stored first cropped image")
                    else:
                        # This is the second image, time to stitch
                        self.second_cropped_image = cropped_frame
                        self.logger.info("Stored second cropped image, starting stitch")
                        
                        try:
                            # Start the stitching process
                            self.analyze_box.stitch(self.first_cropped_image, self.second_cropped_image)
                            
                            # Wait for stitching to complete
                            while self.analyze_box.is_stitching:
                                print(f"Stitching progress: {controller.analyze_box.stitch_progress}%")
                                time.sleep(0.5)
                            
                            # Get the result
                            self.stitched_result = self.analyze_box.get_result()
                            self.logger.info("Stitching completed and result stored")
                            
                            # Reset for next pair of images
                            self.first_cropped_image = None
                            self.second_cropped_image = None
                            
                        except RuntimeError as e:
                            self.logger.error(f"Stitching error: {str(e)}")
                            # If there's an error, we'll try again with the next frames
                            self.first_cropped_image = None
                            self.second_cropped_image = None
            
            # Wait before next check
            time.sleep(self.check_interval)

    def get_current_state(self):
        """
        Get the current state of processing.
        
        Returns:
            dict: A dictionary containing the current state information
        """
        state = {
            "is_processing": self.is_running,
            "has_first_image": self.first_cropped_image is not None,
            "has_second_image": self.second_cropped_image is not None,
            "is_stitching": self.analyze_box.is_stitching,
            "stitch_progress": self.analyze_box.stitch_progress,
            "has_stitched_result": self.stitched_result is not None
        }
        return state

# Example usage:
if __name__ == "__main__":
    # Initialize components
    frame_grabber = FrameGrabber()
    analyze_box = AnalyzeBox()
    controller = ImageProcessingController(frame_grabber, analyze_box)

    # Connect to a video device
    available_devices = frame_grabber.get_available_devices()
    if available_devices:
        device_name = list(available_devices.keys())[1]  # Use the first available device
        result = frame_grabber.initiateVideo(device_name)
        if isinstance(result, str):
            print(f"Error: {result}")
            exit(1)
        
        # Start video capture
        frame_grabber.startVideo()
        
        # Start processing
        controller.start_processing()
        
        try:
            # Run for 30 seconds as an example
            while controller.is_running:
                
                print(f"Stitching progress: {controller.analyze_box.stitch_progress}")
                # Get stitched result if available
                stitched_result = controller.stitched_result
                if stitched_result is not None:
                    # Process or display the stitched result
                    cv2.imshow("Stitched Result", stitched_result)
                
                # Break loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(1)
            
        finally:
            # Clean up
            controller.stop_processing()
            frame_grabber.stopVideo()
            frame_grabber.closeVideo()