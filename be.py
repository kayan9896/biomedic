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
import datetime

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
        self.last = [1, 1]
        self.all_shots = {'shots': []}
        
        self.viewmodel = ProcessingModel()
        
        self.check_interval = 0.1
        
        self.logger = frame_grabber.logger

    def decide_next(self, ResBool, current_stage, current_frame):
        if not ResBool:
            self.errortext='sth'
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
                ResBool, crop_image, err = self.model.analyzeframe(
                    self.current_stage, 
                    self.current_frame,
                    frame,
                    self.calib_data
                )
                
                if not ResBool:
                    # Save the failed frame info regardless of error type
                    version_suffix = "_failed"
                    raw_capture_path = f'shots/rawcaptures/stage{self.current_stage}_frame{self.current_frame}{version_suffix}.png'
                    
                    # Save the raw frame
                    os.makedirs(os.path.join(self.exam_folder, 'shots/rawcaptures'), exist_ok=True)
                    cv2.imwrite(os.path.join(self.exam_folder, raw_capture_path), frame)
                    
                    failed_shot_info = {
                        'stage': self.current_stage,
                        'frame': self.current_frame,
                        'shot_index': self.current_frame-1 if self.current_stage == 1 else self.current_stage * 2 + self.current_frame-1,
                        'view': None,
                        'version': 'failed',
                        'timestamp': datetime.datetime.now().isoformat(),
                        'is_current': False,
                        'raw_capture_file': raw_capture_path,
                        'image_file': None,
                        'landmark_file': None,
                        'recon_index': None,
                        'error_type': 'glyph_error' if err and "Glyph error" in err else 'analysis_error',
                        'error_message': err
                    }

                    shots_file = os.path.join(self.exam_folder, 'shots', 'AllShots.json')
                    os.makedirs(os.path.dirname(shots_file), exist_ok=True)
                    self.all_shots['shots'].append(failed_shot_info)
                    self.save_json(self.all_shots, shots_file)
                    
                    # Continue with existing error handling
                    if err and "Glyph error" in err:
                        print(f"Warning at Stage {self.current_stage}, Frame {self.current_frame}: {err}")
                        self.viewmodel.set_frame(
                            stage=self.current_stage,
                            frame=self.current_frame,
                            image=crop_image
                        )
                        continue
                    else:
                        print(f"Analyzeframe error at Stage {self.current_stage}, Frame {self.current_frame}. Error: {err}")
                        continue
                # Store the frame and metadata in the viewmodel
                self.viewmodel.set_frame(
                    stage=self.current_stage,
                    frame=self.current_frame,
                    image=crop_image
                )

                view_map = {
                    0: 'AP',
                    1: 'RO',
                    2: 'LO',
                    3: None
                }
                current_view = view_map.get(case_number)

                raw_capture_path, image_file_path, landmark_file_path = self.save_shot_info(
                    self.current_stage, 
                    self.current_frame, 
                    current_view
                )

                cv2.imwrite(os.path.join(self.exam_folder, raw_capture_path), frame)
                cv2.imwrite(os.path.join(self.exam_folder, image_file_path), crop_image)
                
                case_number, next_stage, next_frame = self.decide_next(ResBool, self.current_stage, self.current_frame)

                updatenext = False
                # Execute functions based on case number
                match case_number:
                    case 0:
                        try:
                            if self.current_stage == 1:
                                success, phantom_result, error = self.model.analyze_phantom(self.current_stage, self.current_frame, crop_image, "AP")
                                if not success:
                                    raise Exception(error)
                                distort, camcalib, image = phantom_result
                                crop_image = image
                            
                                # Save distortion data
                                dist_index = (self.current_stage - 1) * 2 + self.current_frame
                                dist_path = os.path.join(self.exam_folder, 'reference', 'distortion', f'dist{dist_index}.json')
                                self.save_json(distort, dist_path)
                                
                                # Update camcalib
                                current_shot_index = self.current_frame-1 if self.current_stage == 1 else self.current_stage * 2 + self.current_frame
                                if current_shot_index is not None: 
                                    camcalib['Reference']['AP']['ShotIndex'] = current_shot_index
                                    camcalib['Reference']['AP']['DistFile'] = dist_path
                                
                                # Save updated camcalib
                                calib_path = os.path.join(self.exam_folder, 'reference/reference_calib.json')
                                self.save_json(camcalib, calib_path)

                            success, landmark, error = self.model.analyze_landmark(self.current_stage, self.current_frame, 'AP')
                            if not success:
                                raise Exception(error)
                            self.save_landmark(self.current_stage, self.current_frame, landmark,crop_image)

                            updatenext = True
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_frame = 1
                            if "analyze_phantom" in str(error):
                                print(f"Phantom analysis failed: {error}")
                                # Handle phantom analysis error
                            elif "analyze_landmark" in str(error):
                                print(f"Landmark analysis failed: {error}")
                                # Handle landmark analysis error
                            else:
                                print(f"Unexpected error: {error}")

                    case 1:
                        try:
                            success, phantom_result, error = self.model.analyze_phantom(self.current_stage, self.current_frame, crop_image, "RO")
                            if not success:
                                raise Exception(error)
                            distort, camcalib, image = phantom_result

                            dist_index = (self.current_stage - 1) * 2 + self.current_frame
                            dist_path = os.path.join(self.exam_folder, 'reference', 'distortion', f'dist{dist_index}.json').replace('\\','/')
                            self.save_json(distort, dist_path)
                            
                            # Update camcalib
                            current_shot_index = self.current_frame-1 if self.current_stage == 1 else self.current_stage * 2 + self.current_frame
                            if current_shot_index is not None: 
                                camcalib['Reference']['RO']['ShotIndex'] = current_shot_index
                                camcalib['Reference']['RO']['DistFile'] = dist_path
                            
                            # Save updated camcalib
                            calib_path = os.path.join(self.exam_folder, 'reference/reference_calib.json')
                            self.save_json(camcalib, calib_path)

                            success, landmark, error = self.model.analyze_landmark(self.current_stage, self.current_frame, 'RO')
                            if not success:
                                raise Exception(error)
                            self.save_landmark(self.current_stage, self.current_frame, landmark,image)

                            if self.model.can_recon():
                                success, recon_result, error = self.model.reconstruct(self.current_stage, 0)
                                if not success:
                                    raise Exception(error)
                                stitchimg, recons = recon_result
                                self.viewmodel.set_stitched(stage=self.current_stage, image=stitchimg)

                                # Update shot information with reconstruction index
                                recon_index = 0 if self.current_stage == 1 else self.current_stage  # or adjust based on your needs
                                
                                # Update for both frames used in reconstruction
                                frame1 = self.current_frame
                                frame2 = self.current_frame - 1
                                
                                # Load and update AllShots.json
                                shots_file = os.path.join(self.exam_folder, 'shots', 'AllShots.json')
                               
                                # Update ReconIndex for both shots used in this reconstruction
                                for shot in self.all_shots['shots']:
                                    if shot['stage'] == self.current_stage:
                                        if shot['frame'] in [frame1, frame2]:
                                            shot['recon_index'] = recon_index if shot['is_current'] else None
                                self.save_json(self.all_shots, shots_file)

                                
                                # Create recons directory if it doesn't exist
                                recons_dir = os.path.join(self.exam_folder, 'recons')
                                os.makedirs(recons_dir, exist_ok=True)
                                recons_path = os.path.join(recons_dir, 'AllRecons.json')
                                self.save_json(recons, recons_path)
                            
                            updatenext = True
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 1
                            self.current_frame = 1
                            if "analyze_phantom" in str(error):
                                print(f"Phantom analysis failed: {error}")
                                # Handle phantom analysis error
                            elif "analyze_landmark" in str(error):
                                print(f"Landmark analysis failed: {error}")
                                # Handle landmark analysis error
                            elif "reconstruct" in str(error):
                                print(f"Reconstruction failed: {error}")
                                # Handle reconstruction error
                            else:
                                print(f"Unexpected error: {error}")

                    case 2:
                        try:
                            success, phantom_result, error = self.model.analyze_phantom(self.current_stage, self.current_frame, crop_image, "LO")
                            if not success:
                                raise Exception(error)
                            distort, camcalib, image = phantom_result

                            dist_index = (self.current_stage - 1) * 2 + self.current_frame
                            dist_path = os.path.join(self.exam_folder, 'reference', 'distortion', f'dist{dist_index}.json').replace('\\','/')
                            self.save_json(distort, dist_path)
                            
                            # Update camcalib
                            current_shot_index = self.current_frame-1 if self.current_stage == 1 else self.current_stage * 2 + self.current_frame
                            if current_shot_index is not None: 
                                camcalib['Reference']['LO']['ShotIndex'] = current_shot_index  # Changed from LO to AP
                                camcalib['Reference']['LO']['DistFile'] = dist_path
                            
                            # Save updated camcalib
                            calib_path = os.path.join(self.exam_folder, 'reference/reference_calib.json')
                            self.save_json(camcalib, calib_path)

                            success, landmark, error = self.model.analyze_landmark(self.current_stage, self.current_frame, 'LO')  # Changed from LO to AP
                            if not success:
                                raise Exception(error)
                            self.save_landmark(self.current_stage, self.current_frame, landmark,image)

                            if self.model.can_recon():
                                success, recon_result, error = self.model.reconstruct(self.current_stage, 1)  # Changed from 0 to 1 for the second pair of images
                                if not success:
                                    raise Exception(error)
                                stitchimg, recons = recon_result
                                self.viewmodel.set_stitched(stage=self.current_stage, image=stitchimg)

                                # Update shot information with reconstruction index
                                recon_index = 0 if self.current_stage == 1 and self.current_frame < 3 else self.current_stage  # or adjust based on your needs
                                
                                # Update for both frames used in reconstruction
                                frame1 = self.current_frame
                                frame2 = self.current_frame - 1
                                
                                # Load and update AllShots.json
                                shots_file = os.path.join(self.exam_folder, 'shots', 'AllShots.json')
                            
                                # Update ReconIndex for both shots used in this reconstruction
                                for shot in self.all_shots['shots']:
                                    if shot['stage'] == self.current_stage:
                                        if shot['frame'] in [frame1, frame2]:
                                            shot['recon_index'] = recon_index if shot['is_current'] else None
                                self.save_json(self.all_shots, shots_file)
                                
                                
                                # Create recons directory if it doesn't exist
                                recons_dir = os.path.join(self.exam_folder, 'recons')
                                os.makedirs(recons_dir, exist_ok=True)
                                recons_path = os.path.join(recons_dir, 'AllRecons.json')
                                self.save_json(recons, recons_path)
                                
                                success, result, error = self.model.analyzeref()
                                all_results_path = os.path.join(self.exam_folder, 'results', 'AllResults.json')
                                os.makedirs(os.path.dirname(all_results_path), exist_ok=True)
                                self.save_json(result, all_results_path)
                                if not success:
                                    raise Exception(error)
                            
                            updatenext = True
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 1
                            self.current_frame = 1
                            if "analyze_phantom" in str(error):
                                print(f"Phantom analysis failed: {error}")
                            elif "analyze_landmark" in str(error):
                                print(f"Landmark analysis failed: {error}")
                            elif "reconstruct" in str(error):
                                print(f"Reconstruction failed: {error}")
                            elif "analyzeref" in str(error):
                                print(f"Reference analysis failed: {error}")
                            else:
                                print(f"Unexpected error: {error}")
                    case 3:
                        try:
                            # Analyze landmark
                            success, landmark, error = self.model.analyze_landmark(self.current_stage, self.current_frame, crop_image)
                            if not success:
                                raise Exception(error)
                            self.save_landmark(self.current_stage, self.current_frame, landmark, crop_image)
                            
                            # Reconstruct
                            if self.model.can_recon():
                                success, recon_result, error = self.model.reconstruct(self.current_stage, 0)
                                if not success:
                                    raise Exception(error)
                                stitchimg, recons = recon_result
                                self.viewmodel.set_stitched(stage=self.current_stage, image=stitchimg)
                                
                                # Update shot information with reconstruction index
                                recon_index = 0 if self.current_stage == 1 else self.current_stage  # or adjust based on your needs
                                
                                # Update for both frames used in reconstruction
                                frame1 = self.current_frame
                                frame2 = self.current_frame - 1
                                
                                # Load and update AllShots.json
                                shots_file = os.path.join(self.exam_folder, 'shots', 'AllShots.json')
                            
                                # Update ReconIndex for both shots used in this reconstruction
                                for shot in self.all_shots['shots']:
                                    if shot['stage'] == self.current_stage:
                                        if shot['frame'] in [frame1, frame2]:
                                            shot['recon_index'] = recon_index if shot['is_current'] else None
                                self.save_json(self.all_shots, shots_file)
                                
                                # Create recons directory if it doesn't exist
                                recons_dir = os.path.join(self.exam_folder, 'recons')
                                os.makedirs(recons_dir, exist_ok=True)
                                recons_path = os.path.join(recons_dir, 'AllRecons.json')
                                self.save_json(recons, recons_path)
                            
                            # Analyze cup
                            success, data, error = self.model.analyzecup()
                            if success:
                                updatenext = True
                                self.viewmodel.set_stitched(stage=self.current_stage, image=data[0])
                                all_results_path = os.path.join(self.exam_folder, 'results', 'AllResults.json')
                                os.makedirs(os.path.dirname(all_results_path), exist_ok=True)
                                self.save_json(data[1], all_results_path)
                            else:
                                self.errortext = error
                                self.current_stage = 2
                                self.current_frame = 1
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 2
                            self.current_frame = 1
                            if "analyze_landmark" in str(error):
                                print(f"Landmark analysis failed: {error}")
                            elif "reconstruct" in str(error):
                                print(f"Reconstruction failed: {error}")
                            elif "analyzecup" in str(error):
                                print(f"Cup analysis failed: {error}")
                            else:
                                print(f"Unexpected error in case 3: {error}")

                    case 4:
                        try:
                            # Analyze landmark
                            success, landmark, error = self.model.analyze_landmark(self.current_stage, self.current_frame, crop_image)
                            if not success:
                                raise Exception(error)
                            self.save_landmark(self.current_stage, self.current_frame, landmark, crop_image)
                            
                            # Reconstruct
                            if self.model.can_recon():
                                success, recon_result, error = self.model.reconstruct(self.current_stage, 0)
                                if not success:
                                    raise Exception(error)
                                stitchimg, recons = recon_result
                                self.viewmodel.set_stitched(stage=self.current_stage, image=stitchimg)

                                # Update shot information with reconstruction index
                                recon_index = 0 if self.current_stage == 1 else self.current_stage  # or adjust based on your needs
                                
                                # Update for both frames used in reconstruction
                                frame1 = self.current_frame
                                frame2 = self.current_frame - 1
                                
                                # Load and update AllShots.json
                                shots_file = os.path.join(self.exam_folder, 'shots', 'AllShots.json')
                            
                               
                                # Update ReconIndex for both shots used in this reconstruction
                                for shot in self.all_shots['shots']:
                                    if shot['stage'] == self.current_stage:
                                        if shot['frame'] in [frame1, frame2]:
                                            shot['recon_index'] = recon_index if shot['is_current'] else None
                                self.save_json(self.all_shots, shots_file)
                                
                                # Create recons directory if it doesn't exist
                                recons_dir = os.path.join(self.exam_folder, 'recons')
                                os.makedirs(recons_dir, exist_ok=True)
                                recons_path = os.path.join(recons_dir, 'AllRecons.json')
                                self.save_json(recons, recons_path)
                            
                            # Analyze trial
                            success, data, error = self.model.analyzetrial()
                            if success:
                                updatenext = True
                                self.viewmodel.set_stitched(stage=self.current_stage, image=data[0])
                                all_results_path = os.path.join(self.exam_folder, 'results', 'AllResults.json')
                                os.makedirs(os.path.dirname(all_results_path), exist_ok=True)
                                self.save_json(data[1], all_results_path)
                            else:
                                self.errortext = error
                                self.current_stage = 3
                                self.current_frame = 1
                        except Exception as error:
                            self.errortext = str(error)
                            self.current_stage = 3
                            self.current_frame = 1
                            if "analyze_landmark" in str(error):
                                print(f"Landmark analysis failed: {error}")
                            elif "reconstruct" in str(error):
                                print(f"Reconstruction failed: {error}")
                            elif "analyzetrial" in str(error):
                                print(f"Trial analysis failed: {error}")
                            else:
                                print(f"Unexpected error in case 4: {error}")
                
                # Update stage and frame for next iteration
                if updatenext:
                    self.last = [self.current_stage, self.current_frame]
                    self.current_stage = next_stage
                    self.current_frame = next_frame
                    

    def retake(self):
        self.current_stage, self.current_frame = self.last

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
            
            ref_dir = 'reference'
            os.makedirs(os.path.join(self.exam_folder, ref_dir), exist_ok=True)

            # Load calibration data
            self.calib_data = device_config
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

    def save_json(self, data, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def save_landmark(self, stage, frame, landmark_data,img):
        """Save landmark data to a unique file for each stage and frame"""
        landmark_folder = os.path.join(self.exam_folder, 'shots', 'landmarks')
        os.makedirs(landmark_folder, exist_ok=True)
        
        landmark_file = f'landmark_stage{stage}_frame{frame}.json'
        landmark_path = os.path.join(landmark_folder, landmark_file)
        
        self.save_json(landmark_data, landmark_path)
        
        # Update viewmodel metadata
        self.viewmodel.set_frame(
            stage=stage, 
            frame=frame, 
            image=img,  
            metadata={'landmark_file': landmark_file, **landmark_data}
        )
        
    def save_shot_info(self, stage, frame, view, recon_index=None):
        # Calculate shot index based on stage and frame
        if stage == 1:
            shot_index = frame - 1
        else:
            shot_index = (stage * 2) + (frame - 1)

        # Get the current version number for this stage/frame combination
        current_version = 1
        for shot in self.all_shots['shots']:
            if shot['stage'] == stage and shot['frame'] == frame:
                current_version = max(current_version, shot['version'] + 1)
                # Mark previous versions as not current
                if shot['is_current']:
                    shot['is_current'] = False

        # Define file paths with version numbers
        version_suffix = f'_v{current_version}'
        raw_capture_path = f'shots/rawcaptures/stage{stage}_frame{frame}{version_suffix}.png'
        image_file_path = f'shots/images/stage{stage}_frame{frame}{version_suffix}.png'
        landmark_file_path = f'landmarks/stage{stage}_frame{frame}{version_suffix}.json'

        # Create shot info dictionary
        shot_info = {
            'stage': stage,
            'frame': frame,
            'shot_index': shot_index,
            'view': view,
            'version': current_version,
            'timestamp': datetime.datetime.now().isoformat(),
            'is_current': True,
            'raw_capture_file': raw_capture_path,
            'image_file': image_file_path,
            'landmark_file': landmark_file_path,
            'recon_index': recon_index
        }

        # Update local dictionary
        self.all_shots['shots'].append(shot_info)
        
        # Save to file
        shots_file = os.path.join(self.exam_folder, 'shots', 'AllShots.json')
        os.makedirs(os.path.dirname(shots_file), exist_ok=True)
        self.save_json(self.all_shots, shots_file)

        return raw_capture_path, image_file_path, landmark_file_path
