import threading
import time
from typing import Optional
import numpy as np
import cv2
from ab import AnalyzeBox
from fg import FrameGrabber
from mod import ProcessingModel

class ImageProcessingController:
    def __init__(self, frame_grabber: 'FrameGrabber', analyze_box: 'AnalyzeBox'):
        self.frame_grabber = frame_grabber
        self.analyze_box = analyze_box
        
        self.is_running = False
        self.process_thread = None
        self.stitch_thread = None
        
        # Use the new ProcessingModel instead of individual variables
        self.model = ProcessingModel()
        
        self.check_interval = 0.1
        self.is_stitching = False
        
        self.logger = frame_grabber.logger

    def _stitch_worker(self):
        """Worker function to run stitching in a separate thread"""
        try:
            current_attempt = self.model.current_attempt
            if current_attempt and current_attempt.first_cropped_image is not None and current_attempt.second_cropped_image is not None:
                stitched_result = self.analyze_box.stitch(
                    current_attempt.first_cropped_image, 
                    current_attempt.second_cropped_image
                )
                self.model.set_stitched_result(stitched_result)
                self.logger.info("Stitching completed and result stored")
            else:
                self.logger.error("Cannot stitch: missing first or second image")
        except Exception as e:
            self.logger.error(f"Error during stitching: {str(e)}")
        finally:
            self.is_stitching = False

    def _process_loop(self):
        """Main processing loop that checks for new frames and processes them."""
        #self.model.new_attempt()  # Start a new attempt when processing begins
        
        while self.is_running:
            if self.frame_grabber._is_new_frame_available and not self.is_stitching:
                frame = self.frame_grabber.fetchFrame()
                if frame is not None:
                    cropped_frame = self.analyze_box.crop_center(frame)
                    current_attempt = self.model.current_attempt
                    
                    if current_attempt.first_cropped_image is None:
                        self.model.set_first_image(cropped_frame)
                        self.logger.info("Stored first cropped image")
                    elif current_attempt.second_cropped_image is None:
                        self.model.set_second_image(cropped_frame)
                        self.logger.info("Stored second cropped image, starting stitch")
                        
                        self.is_stitching = True
                        self.stitch_thread = threading.Thread(target=self._stitch_worker)
                        self.stitch_thread.start()
            
            time.sleep(self.check_interval)

    def get_current_state(self):
        """Get the current state of processing."""
        current_attempt = self.model.current_attempt
        state = {
            "is_processing": self.is_running,
            "has_first_image": current_attempt and current_attempt.first_cropped_image is not None,
            "has_second_image": current_attempt and current_attempt.second_cropped_image is not None,
            "is_stitching": self.is_stitching,
            "stitch_progress": self.analyze_box._stitch_progress if hasattr(self.analyze_box, '_stitch_progress') else 0,
            "has_stitched_result": current_attempt and current_attempt.stitched_result is not None
        }
        return state

    def get_attempt_images(self, index: Optional[int] = None):
        """Get images for a specific attempt or current attempt"""
        if index is not None:
            attempt = self.model.get_attempt(index)
        else:
            attempt = self.model.get_current_attempt()
            
        if attempt is None:
            return None
            
        return {
            "first_image": attempt.first_cropped_image,
            "second_image": attempt.second_cropped_image,
            "stitched_result": attempt.stitched_result,
            "timestamp": attempt.timestamp
        }

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

    def start(self, device_name: str):
        """
        Connect to a video device and start processing.
        Returns True on success, error message on failure.
        """
        # Connect to the video device
        result = self.frame_grabber.initiateVideo(device_name)
        if isinstance(result, str):
            return result
        
        # Start video capture and processing
        self.frame_grabber.startVideo()
        self.start_processing()
        return True

    def stop(self):
        """Stop video capture and frame processing"""
        self.stop_processing()
        self.frame_grabber.stopVideo()
        self.frame_grabber.closeVideo()


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