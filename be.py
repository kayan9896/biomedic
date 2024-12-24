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
        self.stitch_thread = None  # New thread for stitching
        
        # Model storage
        self.first_cropped_image = None
        self.second_cropped_image = None
        self.stitched_result = None
        
        self.check_interval = 0.1  # Check for new frames every 100ms
        self.is_stitching = False  # Flag to indicate stitching in progress
        
        self.logger = frame_grabber.logger  # Reuse the logger from frame_grabber

    def _stitch_worker(self):
        """Worker function to run stitching in a separate thread"""
        try:
            self.stitched_result = self.analyze_box.stitch(
                self.first_cropped_image, 
                self.second_cropped_image
            )
            self.logger.info("Stitching completed and result stored")
        except Exception as e:
            self.logger.error(f"Error during stitching: {str(e)}")
            self.stitched_result = None
        finally:
            self.is_stitching = False
            # Reset for next pair of images
            self.first_cropped_image = None
            self.second_cropped_image = None

    def _process_loop(self):
        """Main processing loop that checks for new frames and processes them."""
        while self.is_running:
            if self.frame_grabber._is_new_frame_available and not self.is_stitching:
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
                        
                        # Start the stitching process in a separate thread
                        self.is_stitching = True
                        self.stitch_thread = threading.Thread(target=self._stitch_worker)
                        self.stitch_thread.start()
            
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
            "is_stitching": self.is_stitching,
            "stitch_progress": self.analyze_box._stitch_progress if hasattr(self.analyze_box, '_stitch_progress') else 0,
            "has_stitched_result": self.stitched_result is not None
        }
        return state

    def stop_processing(self):
        """Stop the frame processing loop."""
        if not self.is_running:
            self.logger.warning("Processing is not running")
            return
        
        self.is_running = False
        if self.process_thread:
            self.process_thread.join()
            self.process_thread = None
        
        # Wait for stitching to complete if it's in progress
        if self.is_stitching and self.stitch_thread:
            self.stitch_thread.join()
            self.stitch_thread = None
        
        self.logger.info("Stopped image processing")

    def start_processing(self):
        """Start the frame processing loop in a separate thread."""
        if self.is_running:
            self.logger.warning("Processing is already running")
            return
        
        self.is_running = True
        self.process_thread = threading.Thread(target=self._process_loop)
        self.process_thread.start()
        self.logger.info("Started image processing")


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
        
        cv2.namedWindow('Stitched Result', cv2.WINDOW_NORMAL)
    
        try:
            while True:
                # Check if we have a new stitched result
                if controller.stitched_result is not None:
                    # Display the stitched result
                    cv2.imshow('Stitched Result', controller.stitched_result)
                    
                    # Reset the stitched result in the controller
                    controller.stitched_result = None
                
                # Display current progress
                state = controller.get_current_state()
                if state['is_stitching']:
                    print(f"Stitching progress: {state['stitch_progress']:.2f}%")
                
                # Check for 'q' key press to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("Program interrupted by user")
        
        finally:
            # Clean up
            controller.stop_processing()
            frame_grabber.stopVideo()
            frame_grabber.closeVideo()
            cv2.destroyAllWindows()
            print("Program ended")