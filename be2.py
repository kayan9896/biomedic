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
from exam import Exam
from panel import IMU3

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
        
        # Initialize based on configuration
        self.on_simulation = self.config.get("on_simultation", True)
        self.mode = self.config.get("mode", 0)
        self.video_connected = False
        
        self.viewmodel = ProcessingModel()
        self.exam = Exam()
        self.uistates = None
        self.check_interval = 0.1
        
        self.logger = frame_grabber.logger
        
        # Initialize IMU if enabled in config
        self.imu = None
        if self.config.get("imu_on", True):
            self.imu = IMU3(self.viewmodel)
            imu_port = self.config.get("imu_port", "COM3")
            
    
    def imuonob(self):
        return (not self.imuonap()) and (-50<=self.imu.rotation_angle and self.imu.rotation_angle<=50)
    def imuonap(self):
        return -20<=self.imu.rotation_angle<=20

    def get_states(self):
        states = self.viewmodel.states
        states['is_processing'] = self.model.is_processing
        states['progress'] = self.model.progress
        return states

    def update_landmarks(self, l, r, stage):
        
        if stage == 0:
            self.model.data['hp1-ap']['metadata'] = l
            self.model.data['hp1-ob']['metadata'] = r
            print(stage,l,r)
        if stage == 1:
            self.model.data['hp2-ap']['metadata'] = l
            self.model.data['hp2-ob']['metadata'] = r
        if stage == 2:
            self.model.data['cup-ap']['metadata'] = l
            self.model.data['cup-ob']['metadata'] = r
        if stage == 3:
            self.model.data['tri-ap']['metadata'] = l
            self.model.data['tri-ob']['metadata'] = r
        
        
        self.uistates = 'landmarks' if self.scn[:3] != 'frm' else 'None'
        self.viewmodel.imgs[0]['metadata'] = l
        self.viewmodel.imgs[1]['metadata'] = r
        

    def connect_video(self):
        """
        Connect to the video device and start video capture
        
        Returns:
            Dict: Result with success status and message
        """
        # Get device name from config
        device = self.config.get("framegrabber_device", "OBS Virtual Camera")
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
            
            frame = self.update_backendstates()
            if self.uistates == 'edit': 
                continue
            newscn = self.eval_modelscnario(frame)
            
            if newscn == self.scn or newscn[-3:] == 'end':
                continue
            
            dataforsave, dataforvm, image = self.model.exec(newscn, frame)
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
                    if self.imuonap():
                        return 'frm:hp1-ap:bgn'
                    if self.imuonob():
                        return 'frm:hp1-ob:bgn' 
                return self.scn

            case 'frm:hp1-ap:end'| 'frm:hp1-ob:end':
                if self.model.data['hp1-ap']['success'] and self.model.data['hp1-ob']['success']:
                    return 'rcn:hmplv1:bgn'
                else:
                    if frame is not None:
                        if self.imuonap():
                            return 'frm:hp1-ap:bgn'
                        if self.imuonob():
                            return 'frm:hp1-ob:bgn'
                    return self.scn
            
            case 'rcn:hmplv1:end':
                if self.model.data['hmplv1']['success']:
                    #user goes next
                    if self.uistates == 'next':                        
                        if frame is not None:
                            self.uistates = None
                            if self.imuonap():
                                return 'frm:hp2-ap:bgn'
                            if self.imuonob():
                                return 'frm:hp2-ob:bgn'
                    
                #sucess or not, user can either edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:hmplv1:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.imuonap():
                        self.model.data['hp1-ap']['success'] = None
                        return 'frm:hp1-ap:bgn'
                    if self.imuonob():
                        self.model.data['hp1-ob']['success'] = None
                        return 'frm:hp1-ob:bgn'

                #otherwise, stay at the end stage
                return self.scn
            
            case 'frm:hp2-ap:end'| 'frm:hp2-ob:end':
                if self.model.data['hp2-ap']['success'] and self.model.data['hp2-ob']['success']:
                    return 'rcn:hmplv2:bgn'
                else:
                    if frame is not None:
                        if self.imuonap():
                            return 'frm:hp2-ap:bgn'
                        if self.imuonob():
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
                    if self.imuonap():
                        self.model.data['hp2-ap']['success'] = None
                        return 'frm:hp2-ap:bgn'
                    if self.imuonob():
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
                            if self.imuonap():
                                return 'frm:cup-ap:bgn'
                            if self.imuonob():
                                return 'frm:cup-ob:bgn'
                    if self.uistates == 'skip':                        
                        if frame is not None:
                            self.uistates = None
                            if self.imuonap():
                                return 'frm:tri-ap:bgn'
                            if self.imuonob():
                                return 'frm:tri-ob:bgn'

                    #reg succeeds, user can still edit landmarks changes, redo recon
                    if self.uistates == 'landmarks':
                        self.uistates = None
                        return 'rcn:hmplv2:bgn'

                    #user does nothing/ editing
                    #they can retake
                    if frame is not None:
                        if self.imuonap():
                            self.model.data['hp2-ap']['success'] = None
                            return 'frm:hp2-ap:bgn'
                        if self.imuonob():
                            self.model.data['hp2-ob']['success'] = None
                            return 'frm:hp2-ob:bgn'
                            
                else:
                    #reference fails to reg, force to restart
                    if self.uistates == 'restart':                        
                        if frame is not None:
                            self.uistates = None
                            if self.imuonap():
                                return 'frm:hp1-ap:bgn'
                            if self.imuonob():
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
                        if self.imuonap():
                            return 'frm:cup-ap:bgn'
                        if self.imuonob():
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
                    if self.imuonap():
                        self.model.data['cup-ap']['success'] = None
                        return 'frm:cup-ap:bgn'
                    if self.imuonob():
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
                            if self.imuonap():
                                return 'frm:tri-ap:bgn'
                            if self.imuonob():
                                return 'frm:tri-ob:bgn'

                #reg succeeds or not, user can still edit landmarks changes, redo recon
                if self.uistates == 'landmarks':
                    self.uistates = None
                    return 'rcn:acecup:bgn'

                #user does nothing/ editing
                #they can retake
                if frame is not None:
                    if self.imuonap():
                        self.model.data['cup-ap']['success'] = None
                        return 'frm:cup-ap:bgn'
                    if self.imuonob():
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
                        if self.imuonap():
                            return 'frm:tri-ap:bgn'
                        if self.imuonob():
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
                    if self.imuonap():
                        self.model.data['tri-ap']['success'] = None
                        return 'frm:tri-ap:bgn'
                    if self.imuonob():
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
                    if self.imuonap():
                        self.model.data['tri-ap']['success'] = None
                        return 'frm:tri-ap:bgn'
                    if self.imuonob():
                        self.model.data['tri-ob']['success'] = None
                        return 'frm:tri-ob:bgn'
                            
                return self.scn

                    
