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
from imu2 import IMU2
from exam import Exam
from panel import Panel

class ImageProcessingController:
    def __init__(self, frame_grabber: 'FrameGrabber', analyze_box: 'AnalyzeBox', config = None):
        self.frame_grabber = frame_grabber
        self.model = analyze_box
        self.current_stage = 1
        self.current_frame = 1
        self.is_running = False
        self.process_thread = None
        
        # Get configuration
        self.config = config
        
        self.panel = None
        # Initialize based on configuration
        self.on_simulation = self.config.get("on_simulation", False) 
        self.autocollect = self.config.get('framegrabber_autocollect', True)
        self.ai_mode = self.config.get("ai_mode", True)
        self.model.ai_mode = self.ai_mode
        self.tracking = True
        self.video_connected = False
        
        self.viewmodel = ProcessingModel(config)
        self.exam = Exam()
        self.pause_states= None
        self.uistates = None
        self.do_capture = False
        self.check_interval = 0.1
        
        self.logger = frame_grabber.logger
        
        # Initialize IMU if enabled in config
        
        if self.config.get("imu_on", True):
            imu_port = self.config.get("imu_port", "COM3")
            self.imu = IMU2(imu_port)
            
        if self.on_simulation:
            self.panel = Panel(self, config=self.config)
            self.model.on_simulation = self.on_simulation



    def get_states(self):
        states = self.viewmodel.states
        states['is_processing'] = self.model.is_processing
        states['progress'] = self.model.progress
        states['ai_mode'] = self.ai_mode
        states['autocollect'] = self.autocollect 
        states['tracking'] = self.tracking 
        # Update video_on based on frame_grabber state
        if hasattr(self, 'frame_grabber'):
            is_connected = getattr(self.frame_grabber, 'is_connected', False)
            is_running = getattr(self.frame_grabber, 'is_running', False)
            states['video_on'] = is_connected and is_running
        
        # Update imu_on based on IMU is_connected
        states['imu_on'] = getattr(self.imu, 'is_connected', True)  # Default to True if property not found

        if self.tracking:
            states['angle'] = self.imu.angle
            states['rotation_angle'] = self.imu.rotation_angle
            states['active_side'] = self.imu.activeside()
            states.update(self.imu.get_all(states['stage']))

        return states

    def get_image_with_metadata(self):
        if self.viewmodel.states['active_side'] == 'ap':
            return self.viewmodel.imgs[0]
        elif self.viewmodel.states['active_side'] == 'ob':
            return self.viewmodel.imgs[1]

    def update_landmarks(self, l, r, stage):
        
        if stage == 0:
            self.model.data['hp1-ap']['metadata']['metadata'] = l
            self.model.data['hp1-ob']['metadata']['metadata'] = r
            print(stage,l,r)
        if stage == 1:
            self.model.data['hp2-ap']['metadata']['metadata'] = l
            self.model.data['hp2-ob']['metadata']['metadata'] = r
        if stage == 2:
            self.model.data['cup-ap']['metadata']['metadata'] = l
            self.model.data['cup-ob']['metadata']['metadata'] = r
        if stage == 3:
            self.model.data['tri-ap']['metadata']['metadata'] = l
            self.model.data['tri-ob']['metadata']['metadata'] = r
        
        
        self.uistates = 'landmarks' if 'ap' not in self.scn else 'None'
        self.pause_states = None
        self.viewmodel.imgs[0]['metadata']['metadata'] = l
        self.viewmodel.imgs[1]['metadata']['metadata'] = r
        

    def connect_video(self):
        """
        Connect to the video device and start video capture
        
        Returns:
            Dict: Result with success status and message
        """
        # Get device name from config
        device = self.config.get("framegrabber_device", "OBS Virtual Camera")
        if self.on_simulation:
            # Use the framegrabber connection state from Panel
            is_connected = False
            is_running = False
            
            if hasattr(self, 'frame_grabber'):
                is_connected = getattr(self.frame_grabber, 'is_connected', False)
                is_running = getattr(self.frame_grabber, 'is_running', False)
            
            connected = is_connected and is_running
            
            if connected:
                return {
                    "connected": True,
                    "message": f"Successfully connected to {device}"
                }
            else:
                return {
                    "connected": False,
                    "message": "Failed to connect to camera device"
                }
        if self.video_connected:
            return {
                "connected": True,
                "message": f"Successfully connected to {device}"
            }
        try: 
            # Initiate video connection
            result = self.frame_grabber.initiateVideo(device)
            if isinstance(result, str):
                self.video_connected = False
                return {
                    "connected": False,
                    "message": f"Failed to connect to video device: {result}"
                }
            
            # Start video capture
            start_result = self.frame_grabber.startVideo(self.config.get("framegrabber_frequency", 30.0))
            if isinstance(start_result, str):
                self.video_connected = False
                return {
                    "connected": False,
                    "message": f"Failed to start video capture: {start_result}"
                }
            
            self.video_connected = True
            return {
                "connected": True,
                "message": f"Successfully connected to {device}"
            }
        
        except Exception as e:
            self.video_connected = False
            self.logger.error(f"Error connecting to video: {str(e)}")
            return {
                "connected": False,
                "message": f"Error connecting to video: {str(e)}"
            }


    def run2(self):
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
            if self.do_capture:
                frame = self.frame_grabber.last_frame
                self.do_capture = False
            else:
                # Normal processing
                frame = self.update_backendstates()
            
            if self.pause_states == 'edit': 
                time.sleep(1)
                continue

            newscn = self.eval_modelscnario(frame)
            
            if newscn == self.scn or newscn[-3:] == 'end':
                continue
            self.imu.confirm_save()
            dataforsave, dataforvm, image = self.model.exec(newscn, frame, self.imu.angle, self.imu.rotation_angle)
            print(frame,image,dataforvm,newscn)
            self.scn = newscn[:-3] + 'end'
            self.viewmodel.update(dataforvm, image)
            self.exam.save(dataforsave, image, frame)

    def update_backendstates(self):
        if not self.frame_grabber._is_new_frame_available or self.model.is_processing:
            return None
        return self.frame_grabber.fetchFrame()

    def eval_modelscnario(self, frame):
        match self.scn:
            case 'init':
                if frame is not None:
                    if self.viewmodel.states['active_side'] == 'ap':
                        return 'frm:hp1-ap:bgn'
                    if self.viewmodel.states['active_side'] == 'ob':
                        return 'frm:hp1-ob:bgn' 
                return self.scn

            case 'frm:hp1-ap:end'| 'frm:hp1-ob:end':
                
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:hmplv1:bgn'

                if self.model.data['hp1-ap']['success'] and self.model.data['hp1-ob']['success']:
                    return 'rcn:hmplv1:bgn'
                else:
                    if frame is not None:
                        if self.viewmodel.states['active_side'] == 'ap':
                            return 'frm:hp1-ap:bgn'
                        if self.viewmodel.states['active_side'] == 'ob':
                            return 'frm:hp1-ob:bgn'
                    return self.scn
            
            case 'rcn:hmplv1:end':
                if self.model.data['hmplv1']['success']:
                    #user goes next
                    if self.uistates == 'next':                        
                        if frame is not None:
                            self.uistates = None
                            if self.viewmodel.states['active_side'] == 'ap':
                                return 'frm:hp2-ap:bgn'
                            if self.viewmodel.states['active_side'] == 'ob':
                                return 'frm:hp2-ob:bgn'
                    
                #sucess or not, user can either edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:hmplv1:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.viewmodel.states['active_side'] == 'ap':
                        self.model.data['hp1-ap']['success'] = None
                        return 'frm:hp1-ap:bgn'
                    if self.viewmodel.states['active_side'] == 'ob':
                        self.model.data['hp1-ob']['success'] = None
                        return 'frm:hp1-ob:bgn'

                #otherwise, stay at the end stage
                return self.scn
            
            case 'frm:hp2-ap:end'| 'frm:hp2-ob:end':
                if self.model.data['hp2-ap']['success'] and self.model.data['hp2-ob']['success']:
                    return 'rcn:hmplv2:bgn'
                else:
                    if frame is not None:
                        if self.viewmodel.states['active_side'] == 'ap':
                            return 'frm:hp2-ap:bgn'
                        if self.viewmodel.states['active_side'] == 'ob':
                            return 'frm:hp2-ob:bgn'
                    return self.scn
                
            case 'rcn:hmplv2:end':
                if self.model.data['hmplv2']['success']:
                    return 'reg:pelvis:bgn'
                    
                #fail, user can either edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:hmplv2:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.viewmodel.states['active_side'] == 'ap':
                        self.model.data['hp2-ap']['success'] = None
                        return 'frm:hp2-ap:bgn'
                    if self.viewmodel.states['active_side'] == 'ob':
                        self.model.data['hp2-ob']['success'] = None
                        return 'frm:hp2-ob:bgn'

                #otherwise, stay at the end stage
                return self.scn

            case 'reg:pelvis:end':
                if self.model.data['pelvis']['success']:
                    #user goes next
                    if self.uistates == 'next':                        
                        if frame is not None:
                            self.uistates = None
                            if self.viewmodel.states['active_side'] == 'ap':
                                return 'frm:cup-ap:bgn'
                            if self.viewmodel.states['active_side'] == 'ob':
                                return 'frm:cup-ob:bgn'
                    if self.uistates == 'skip':                        
                        if frame is not None:
                            self.uistates = None
                            if self.viewmodel.states['active_side'] == 'ap':
                                return 'frm:tri-ap:bgn'
                            if self.viewmodel.states['active_side'] == 'ob':
                                return 'frm:tri-ob:bgn'

                    #reg succeeds, user can still edit landmarks changes, redo recon
                    if self.uistates == 'landmarks':
                        self.uistates = None
                        return 'rcn:hmplv2:bgn'

                    #user does nothing/ editing
                    #they can retake
                    if frame is not None:
                        if self.viewmodel.states['active_side'] == 'ap':
                            self.model.data['hp2-ap']['success'] = None
                            return 'frm:hp2-ap:bgn'
                        if self.viewmodel.states['active_side'] == 'ob':
                            self.model.data['hp2-ob']['success'] = None
                            return 'frm:hp2-ob:bgn'
                            
                else:
                    #reference fails to reg, force to restart
                    if self.uistates == 'restart':                        
                        if frame is not None:
                            self.uistates = None
                            if self.viewmodel.states['active_side'] == 'ap':
                                return 'frm:hp1-ap:bgn'
                            if self.viewmodel.states['active_side'] == 'ob':
                                return 'frm:hp1-ob:bgn'
                return self.scn
            
            case 'frm:cup-ap:end'| 'frm:cup-ob:end':
                if self.uistates == 'next':                        
                    self.model.data['tri-ap'] = self.model.data['cup-ap']
                    self.model.data['tri-ob'] = self.model.data['cup-ob']
                    self.scn = 'frm:tri-ob:end'
                    return self.scn
                if self.model.data['cup-ap']['success'] and self.model.data['cup-ob']['success']:
                    return 'rcn:acecup:bgn'
                else:
                    if frame is not None:
                        if self.viewmodel.states['active_side'] == 'ap':
                            return 'frm:cup-ap:bgn'
                        if self.viewmodel.states['active_side'] == 'ob':
                            return 'frm:cup-ob:bgn'
                    return self.scn

            case 'rcn:acecup:end':
                if self.model.data['acecup']['success']:
                    return 'reg:regcup:bgn'
                    
                #fail, user can either edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:acecup:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.viewmodel.states['active_side'] == 'ap':
                        self.model.data['cup-ap']['success'] = None
                        return 'frm:cup-ap:bgn'
                    if self.viewmodel.states['active_side'] == 'ob':
                        self.model.data['cup-ob']['success'] = None
                        return 'frm:cup-ob:bgn'

                #otherwise, stay at the end stage
                return self.scn

            case 'reg:regcup:end':
                if self.model.data['regcup']['success']:
                    #user goes next
                    if self.uistates == 'next':                        
                        if frame is not None:
                            self.uistates = None
                            if self.viewmodel.states['active_side'] == 'ap':
                                return 'frm:tri-ap:bgn'
                            if self.viewmodel.states['active_side'] == 'ob':
                                return 'frm:tri-ob:bgn'

                #reg succeeds or not, user can still edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:acecup:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.viewmodel.states['active_side'] == 'ap':
                        self.model.data['cup-ap']['success'] = None
                        return 'frm:cup-ap:bgn'
                    if self.viewmodel.states['active_side'] == 'ob':
                        self.model.data['cup-ob']['success'] = None
                        return 'frm:cup-ob:bgn'
                            
                return self.scn

            case 'frm:tri-ap:end'| 'frm:tri-ob:end':
                if self.uistates == 'prev':                        
                    self.model.data['cup-ap'] = self.model.data['tri-ap'] 
                    self.model.data['cup-ob'] = self.model.data['tri-ob'] 
                    self.scn = 'frm:cup-ob:end'
                    return self.scn
                if self.model.data['tri-ap']['success'] and self.model.data['tri-ob']['success']:
                    return 'rcn:tothip:bgn'
                else:
                    if frame is not None:
                        if self.viewmodel.states['active_side'] == 'ap':
                            return 'frm:tri-ap:bgn'
                        if self.viewmodel.states['active_side'] == 'ob':
                            return 'frm:tri-ob:bgn'
                    return self.scn

            case 'rcn:tothip:end':
                if self.model.data['tothip']['success']:
                    return 'reg:regtri:bgn'
                    
                #fail, user can either edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:tothip:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.viewmodel.states['active_side'] == 'ap':
                        self.model.data['tri-ap']['success'] = None
                        return 'frm:tri-ap:bgn'
                    if self.viewmodel.states['active_side'] == 'ob':
                        self.model.data['tri-ob']['success'] = None
                        return 'frm:tri-ob:bgn'

                #otherwise, stay at the end stage
                return self.scn

            case 'reg:regtri:end':
                #reg succeeds or not, user can still edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:tothip:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.viewmodel.states['active_side'] == 'ap':
                        self.model.data['tri-ap']['success'] = None
                        return 'frm:tri-ap:bgn'
                    if self.viewmodel.states['active_side'] == 'ob':
                        self.model.data['tri-ob']['success'] = None
                        return 'frm:tri-ob:bgn'
                            
                return self.scn

                    
