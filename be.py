import threading
import time
from typing import Optional
import numpy as np
import cv2
import os
from ab import AnalyzeBox
from fg import FrameGrabber
from mod import ProcessingModel
import json

class ImageProcessingController:
    def __init__(self, frame_grabber: 'FrameGrabber', analyze_box: 'AnalyzeBox'):
        self.frame_grabber = frame_grabber
        self.model = analyze_box
        self.mode = 1
        self.current_stage = 1
        self.current_frame = 1
        self.is_running = False
        self.process_thread = None
        self.stitch_thread = None
        self.process_next_frame = True  # Add new flag
        
        # Use the new ProcessingModel instead of individual variables
        self.viewmodel = ProcessingModel()
        
        self.check_interval = 0.1
        
        self.logger = frame_grabber.logger

    def decide_next(self, ResBool, current_stage, current_frame):
        if not ResBool:
            self.errortext=sth
            return 0, current_stage, current_frame
        
        # Stage 1
        if current_stage == 1:
            if current_frame == 1:
                return 0, 1, 2
            elif current_frame == 2:
                return 1, 1, 3  # Call rhp
            elif current_frame == 3:
                return 0, 1, 4
            elif current_frame == 4:
                return 2, 2, 1  # Call rhp and rwp
        
        # Stage 2
        elif current_stage == 2:
            if current_frame == 1:
                return 0, 2, 2
            elif current_frame == 2:
                return 3, 3, 1  # Call analyzecup
        
        # Stage 3
        elif current_stage == 3:
            if current_frame == 1:
                return 0, 3, 2
            elif current_frame == 2:
                return 4, 0, 0  # Call analyzetrial
        
        return 0, current_stage, current_frame

    def run_simulation(self):
        """Set up simulation mode and load mock data."""
        self.mode = 0  # 0 for simulation mode, 1 for normal mode
        self.mockdata = []
        
        # Load mock images from the download folder
        download_path = os.path.join('../', 'Downloads')
        try:
            # Get all files starting with 'drr' and sort them naturally
            files = [f for f in os.listdir(download_path) if f.startswith('drr')]
            files.sort(key=lambda x: int(x.split('(')[1].split(')')[0]) if '(' in x else 0)
            
            for filename in files:
                filepath = os.path.join(download_path, filename)
                img = cv2.imread(filepath)
                if img is not None:
                    metadata_file = 'metadata.json'
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                                                    
                    self.mockdata.append({'img':img,'metadata':metadata})
                else:
                    print(f"Warning: Could not load image {filename}")
            
            if not self.mockdata:
                raise ValueError("No valid mock images found")
            
            print(f"Loaded {len(self.mockdata)} mock images for simulation")
            
        except Exception as e:
            print(f"Error setting up simulation mode: {e}")
            self.mode = 1  # Revert to normal mode if setup fails
            return False
        
        return True

    def stop_simulation(self):
        """Stop simulation and clear mock data."""
        self.mode = 1
        self.mockdata.clear()

    def _process_loop(self):
        case_number = 0
        
        while self.is_running:
            # Ensure we have a current attempt
            if not self.viewmodel.current_attempt:
                print(3)
                continue

            # Get frame based on mode
            if self.mode == 1:  # Normal mode
                if not self.frame_grabber._is_new_frame_available or self.model.is_processing:
                    continue
                frame = self.frame_grabber.fetchFrame()
            else:  # Simulation mode
                if not self.mockdata or self.model.is_processing:
                    continue
                    
                if not self.process_next_frame:
                    time.sleep(0.1)
                    continue
                    
                try:
                    pop = self.mockdata.pop(0)
                    frame = pop['img']
                    metadata = pop['metadata']
                    
                    # Store frame with its metadata
                    self.viewmodel.set_frame(
                        stage=self.current_stage,
                        frame=self.current_frame,
                        image=frame,
                        metadata=metadata
                    )
                    
                    self.process_next_frame = False
                except IndexError:
                    print("Simulation completed: No more mock frames available")
                    self.is_running = False
                    break

            if frame is not None:
                # Get analysis results
                ResBool, image_data, metadata = self.model.analyzeframe(
                    self.current_stage, 
                    self.current_frame,
                    frame
                )
                
                if not ResBool:
                    print(f"Analyzeframe error at Stage {self.current_stage}, Frame {self.current_frame}")
                    continue
                

                # Store the frame in the viewmodel
                self.viewmodel.set_frame(
                    stage=self.current_stage,
                    frame=self.current_frame,
                    image=image_data
                )
                
                case_number, next_stage, next_frame = self.decide_next(ResBool, self.current_stage, self.current_frame)
                
                updatenext = False
                # Execute functions based on case number
                match case_number:
                    case 0:
                        updatenext = True
                    case 1:
                        try:
                            result=self.model.rhp(0)
                            self.viewmodel.set_stitched(stage=self.current_stage, image=result)
                            updatenext = True
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 1
                            self.current_frame = 1
                            print(f"Error in rhp: {error}")
                    case 2:
                        try:
                            self.model.rhp(1)  
                            result=self.model.rwp()
                            self.viewmodel.set_stitched(stage=self.current_stage, image=result)
                            updatenext = True
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 1
                            self.current_frame = 1
                            print(f"Error in rhp/rwp: {error}")
                    case 3:
                        try:
                            cup_bool, data, error = self.model.analyzecup()
                            if cup_bool:
                                updatenext = True
                                self.viewmodel.set_stitched(stage=self.current_stage, image=data)
                            else:
                                self.errortext = error
                                self.current_stage = 2
                                self.current_frame = 1
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 2
                            self.current_frame = 1
                            print(f"Error in analyzecup: {error}")
                    case 4:
                        try:
                            trial_bool, data, error = self.model.analyzetrial()
                            if trial_bool:
                                updatenext = True
                                self.viewmodel.set_stitched(stage=self.current_stage, image=data)
                            else:
                                self.errortext = error
                                self.current_stage = 3
                                self.current_frame = 1
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 3
                            self.current_frame = 1
                            print(f"Error in analyzetrial: {error}")
                
                # Update stage and frame for next iteration
                if updatenext:
                    self.current_stage = next_stage
                    self.current_frame = next_frame


    def get_current_state(self):
        """Get the current state of processing."""
        current_attempt = self.viewmodel.current_attempt
        state = {
            "is_processing": self.model.is_processing,
            "stitch_progress": self.model.stitch_progress,
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

    controller.run_simulation()
    for i in controller.mockdata:
        while True:
            cv2.imshow('',i)
                
            # Check for 'q' key press to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        