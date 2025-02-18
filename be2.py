import threading
import time
from typing import Optional
import numpy as np
import cv2
import os
from ab2 import AnalyzeBox
from fg import FrameGrabber
from mod import ProcessingModel
import json
import shutil
from glob import glob
import datetime
from imu import IMU

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
        self.imu = IMU(self.viewmodel)  # Pass viewmodel to IMU
    
    def imuonob(self):
        return (not self.imuonap()) and (-45<=self.imu.rotation_angle and self.imu.rotation_angle<=45)
    def imuonap(self):
        return -15<=self.imu.rotation_angle<=15

    def get_states(self):
        states = self.viewmodel.states
        states['is_processing'] = self.model.is_processing
        states['progress'] = self.model.progress
        return states

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

    def run2(self):
        result = self.frame_grabber.initiateVideo('OBS Virtual Camera')
        if isinstance(result, str):
            return result
        
        # Start video capture and processing
        self.frame_grabber.startVideo()
        self.start_processing2()
        return True

    def start_processing2(self):
        """Start the frame processing loop in a separate thread."""
        if self.is_running:
            self.logger.warning("Processing is already running")
            return
        
        self.is_running = True
        self.process_thread = threading.Thread(target=self._process_loop)
        self.process_thread.start()
        self.logger.info("Started image processing")

    def _process_loop(self):
        self.scn = 'init'
        while self.is_running:
            frame = self.update_backendstates()
            newscn = self.eval_modelscnario(frame)
            #print(newscn)
            if newscn == self.scn:
                continue
            
            dataforsave, dataforvm, image = self.model.exec(newscn, frame)
            print(frame,image,dataforvm)
            self.scn = newscn[:-3] + 'end'
            self.viewmodel.update(dataforvm, image)

    def update_backendstates(self):
        if not self.frame_grabber._is_new_frame_available or self.model.is_processing:
            return None
        return self.frame_grabber.fetchFrame()

    def eval_modelscnario(self, frame):
        match self.scn:
            case 'init':
                if frame is not None:
                    if self.imuonap():
                        return 'frm:hp1-ap:bgn'
                    if self.imuonob:
                        return 'frm:hp1-ob:bgn' 
                return self.scn

            case 'frm:hp1-ap:end'| 'frm:hp1-ob:end':
                if self.model.data['hp1_ap'] and self.model.data['hp1_ob']:
                    return 'rcn:hmplv1:bgn'
                else:
                    if frame is not None:
                        if self.imuonap():
                            return 'frm:hp1-ap:bgn'
                        if self.imuonob:
                            return 'frm:hp1-ob:bgn'
                    return self.scn
                
