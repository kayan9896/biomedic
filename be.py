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
import shutil
from glob import glob

class ImageProcessingController:
    def __init__(self, frame_grabber: 'FrameGrabber', analyze_box: 'AnalyzeBox'):
        self.frame_grabber = frame_grabber
        self.model = analyze_box
        self.current_stage = 1
        self.current_frame = 1
        self.is_running = False
        self.process_thread = None
        self.stitch_thread = None
        self.process_next_frame = True  
        self._device_configs = {}
        self._calib_folders = {}
        
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
        self.model.mode = 0  # 0 for simulation mode, 1 for normal mode
        self.mockdata = []
        
        # Load mock images from the download folder
        download_path = os.path.join('../../', 'Downloads')
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
        self.model.mode = 1
        self.mockdata.clear()

    def _process_loop(self):
        case_number = 0
        
        while self.is_running:
            if not self.viewmodel.current_attempt:
                print(3)
                continue

            # Get frame based on mode
            if self.model.mode == 1:  # Normal mode
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
                    frame = self.mockdata.pop(0)  # Pop the entire dict
                    self.process_next_frame = False
                except IndexError:
                    print("Simulation completed: No more mock frames available")
                    self.is_running = False
                    break

            if frame is not None:
                # Get analysis results with calibration data
                ResBool, image_data, metadata, Shot = self.model.analyzeframe(
                    self.current_stage, 
                    self.current_frame,
                    frame,
                    self.calib_data
                )
                
                if not ResBool:
                    print(f"Analyzeframe error at Stage {self.current_stage}, Frame {self.current_frame}")
                    continue

                # Save data to exam folder
                try:
                    shots_folder = os.path.join(self.exam_folder, "shots")
                    
                    # Save original frame
                    cv2.imwrite(os.path.join(shots_folder, "rawcaptures", f"stage{self.current_stage}_frame{self.current_frame}.png"), frame)
                    
                    # Save processed image
                    cv2.imwrite(os.path.join(shots_folder, "images", f"stage{self.current_stage}_frame{self.current_frame}.png"), image_data)
                    
                    # Save metadata
                    with open(os.path.join(shots_folder, "landmarks", f"stage{self.current_stage}_frame{self.current_frame}.json"), 'w') as f:
                        json.dump(metadata, f)
                    
                    # Update AllShots.json
                    all_shots_path = os.path.join(shots_folder, "AllShots.json")
                    all_shots = {}
                    if os.path.exists(all_shots_path):
                        with open(all_shots_path, 'r') as f:
                            all_shots = json.load(f)
                    
                    shot_key = f"stage{self.current_stage}_frame{self.current_frame}"
                    all_shots[shot_key] = Shot
                    
                    with open(all_shots_path, 'w') as f:
                        json.dump(all_shots, f)

                except Exception as e:
                    print(f"Error saving shot data: {e}")

                # Store the frame and metadata in the viewmodel
                self.viewmodel.set_frame(
                    stage=self.current_stage,
                    frame=self.current_frame,
                    image=image_data,
                    metadata=metadata
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

    def get_devices(self):
        """Get available calibrated devices and cache their configurations and paths"""
        devices = []
        calibration_dir = "Calibration"  # Adjust path if needed
        
        # Clear existing caches
        self._device_configs.clear()
        self._calib_folders.clear()
        
        # Walk through all subdirectories in Calibration folder
        for root, dirs, files in os.walk(calibration_dir):
            if "device_calib.json" in files:
                file_path = os.path.join(root, "device_calib.json")
                try:
                    with open(file_path, 'r') as f:
                        calib_data = json.load(f)
                        if 'Carm' in calib_data and 'C-arm Model' in calib_data['Carm']:
                            model = calib_data['Carm']['C-arm Model']
                            devices.append(model)
                            # Cache the configuration and folder path
                            self._device_configs[model] = calib_data
                            self._calib_folders[model] = root
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
        
        return list(set(devices))

    def start(self, carm_model: str):
        """
        Connect to a video device based on C-arm model, start processing,
        and set up a new exam folder with calibration files.
        Returns True on success, error message on failure.
        """
        # Check if we need to load configurations
        if not self._device_configs:
            self.get_devices()
        
        # Get the cached config and folder path
        device_config = self._device_configs.get(carm_model)
        calib_folder = self._calib_folders.get(carm_model)
        if not device_config or not calib_folder:
            return f"No configuration found for C-arm model: {carm_model}"
        
        # Get the framegrabber device name from the cached config
        try:
            framegrabber_name = device_config['FrameGrabber']['DeviceName']
        except KeyError:
            return "Invalid configuration: FrameGrabber DeviceName not found"

        # Create new exam folder and copy calibration files
        try:
            self.exam_folder = self._create_new_exam_folder()
            if not self._copy_calib_files(calib_folder, self.exam_folder):
                return "Failed to copy calibration files"
            # Create additional folders for shots
            shots_folder = os.path.join(self.exam_folder, "shots")
            os.makedirs(os.path.join(shots_folder, "rawcaptures"), exist_ok=True)
            os.makedirs(os.path.join(shots_folder, "images"), exist_ok=True)
            os.makedirs(os.path.join(shots_folder, "landmarks"), exist_ok=True)
            
            # Load calibration data
            with open(os.path.join(self.exam_folder, "calib", "device_calib.json"), 'r') as f:
                self.calib_data = json.load(f)
        except Exception as e:
            return f"Failed to set up exam folder: {str(e)}"

        # Connect to the video device
        result = self.frame_grabber.initiateVideo(framegrabber_name)
        if isinstance(result, str):
            return result
        
        # Start video capture and processing
        self.frame_grabber.startVideo()
        self.start_processing()
        return True

    def _create_new_exam_folder(self):
        """Create a new exam folder and return its path"""
        exams_dir = "Exams"  # Adjust path if needed
        os.makedirs(exams_dir, exist_ok=True)
        
        # Find existing exam folders
        existing_exams = glob(os.path.join(exams_dir, "Exam*"))
        existing_numbers = [int(os.path.basename(exam)[4:]) 
                           for exam in existing_exams 
                           if os.path.basename(exam)[4:].isdigit()]
        
        # Determine new exam number
        new_exam_num = max(existing_numbers, default=0) + 1
        new_exam_folder = os.path.join(exams_dir, f"Exam{new_exam_num:02d}")
        
        # Create new exam folder and calib subfolder
        calib_folder = os.path.join(new_exam_folder, "calib")
        os.makedirs(calib_folder)
        
        return new_exam_folder

    def _copy_calib_files(self, source_folder, exam_folder):
        """Copy calibration files to the new exam folder"""
        try:
            calib_folder = os.path.join(exam_folder, "calib")
            
            # Copy device_calib.json
            shutil.copy2(
                os.path.join(source_folder, "device_calib.json"),
                os.path.join(calib_folder, "device_calib.json")
            )
            
            # Copy frame_mask.png
            shutil.copy2(
                os.path.join(source_folder, "frame_mask.png"),
                os.path.join(calib_folder, "frame_mask.png")
            )
            
            return True
        except Exception as e:
            print(f"Error copying calibration files: {str(e)}")
            return False

    def stop(self):
        """Stop video capture and frame processing"""
        self.stop_processing()
        self.frame_grabber.stopVideo()
        self.frame_grabber.closeVideo()

    
