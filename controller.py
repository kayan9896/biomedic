import threading
import time
from typing import Optional
import numpy as np
from PIL import Image
import cv2
import os
from model import Model
from fg import FrameGrabber
from viewmodel import ViewModel
import json
import shutil
from glob import glob
import datetime
from imu2 import IMU2
from exam import Exam
from flask import jsonify

class Controller:
    def __init__(self, config = None, calib = None,  panel = None):
        self.calib = calib
        self.config = config
        self.frame_grabber = FrameGrabber(self.calib["FrameGrabber"])

        self.is_running = False
        self.process_thread = None
        
        # Get configuration
        
        
        self.panel = None
        # Initialize based on configuration
        self.on_simulation = self.config.get("on_simulation", False) 
        self.autocollect = self.config.get('framegrabber_autocollect', True)
        self.ai_mode = self.config.get("ai_mode", True)
        self.model = Model(self.ai_mode, self.on_simulation, self.calib["Model"], self.calib["distortion"], self.calib["gantry"])
        self.is_processing = False
        
        self.viewmodel = ViewModel(config)
        self.exam = Exam(self.calib['folder'])
        self.pause_states= None
        self.uistates = None
        self.do_capture = False
        self.check_interval = 0.1
        
        self.logger = self.frame_grabber.logger
        
        # Initialize IMU if enabled in config
        self.tracking = self.calib['IMU'].get("imu_on", True)
        if self.tracking:
            imu_port = self.calib['IMU'].get("imu_port", "COM3")
            self.imu = IMU2(imu_port, self.calib["IMU"]["ApplyTarget"], self.calib["IMU"]["CarmRangeTilt"], self.calib["IMU"]["CarmRangeRotation"], self.calib["IMU"]["CarmTargetTilt"], self.calib["IMU"]["CarmTargetRot"], tol = self.calib["IMU"]["tol"])
  
        if self.on_simulation:
            self.panel = panel
            self.panel.controller = self

    def restart(self):
        self.uistates = 'restart'
        self.model._resetdata()
        self.scn = 'init'
        self.viewmodel.states['stage'] = 0
        if self.tracking:
            imu_port = self.config.get("imu_port", "COM3")
            self.imu = IMU2(imu_port, self.calib["IMU"]["ApplyTarget"], self.calib["IMU"]["CarmRangeTilt"], self.calib["IMU"]["CarmRangeRotation"], self.calib["IMU"]["CarmTargetTilt"], self.calib["IMU"]["CarmTargetRot"], tol = self.calib["IMU"]["tol"])

    def get_states(self):
        states = self.viewmodel.states
        states['is_processing'] = self.is_processing
        states['progress'] = self.model.progress
        states['ai_mode'] = self.ai_mode
        states['autocollect'] = self.autocollect 
        states['scn'] = self.scn
        # Update video_on based on frame_grabber state
        if hasattr(self, 'frame_grabber'):
            is_connected = getattr(self.frame_grabber, 'is_connected', False)
            is_running = getattr(self.frame_grabber, 'is_running', False)
            states['video_on'] = is_connected and is_running
        
        # Update imu_on based on IMU is_connected
        states['imu_on'] = False if not hasattr(self, 'imu') else getattr(self.imu, 'is_connected', True)  # Default to True if property not found

        if self.tracking:
            states['tilt_angle'] = self.imu.tilt_angle
            states['rotation_angle'] = self.imu.rotation_angle
            states['active_side'] = self.imu.activeside(states['stage'])
            states.update(self.imu.get_all(states['stage']))

        return states
    
    def backend_to_frontend_coords(self, coords, backend_size=1024, frontend_size=960, btof = True, flip_horizontal=False):
        """
        Convert coordinates from backend (1024x1024) to frontend (960x960) scale
        
        Args:
            coords: Can be a single [x,y] coordinate pair or nested structures containing coordinates
            backend_size: Size of the backend image (default 1024)
            frontend_size: Size of the frontend display (default 960)
            flip_horizontal: If True, will flip x-coordinates horizontally (mirror effect)
        
        Returns:
            Converted coordinates in the same structure as input
        """
        scale_factor = frontend_size / backend_size if btof else backend_size / frontend_size
        
        if isinstance(coords, list):
            if len(coords) == 2 and all(isinstance(c, (int, float)) for c in coords):
                # Single [x,y] coordinate pair
                x, y = coords
                
                # Flip horizontally if requested
                if flip_horizontal:
                    x = backend_size - x
                    
                # Scale the coordinates
                x_scaled = x * scale_factor
                y_scaled = y * scale_factor
                
                return [int(x_scaled), int(y_scaled)]
            else:
                # Nested list structure
                return [self.backend_to_frontend_coords(item, backend_size, frontend_size, btof, flip_horizontal) for item in coords]
        elif isinstance(coords, dict):
            # Dictionary structure
            return {k: self.backend_to_frontend_coords(v, backend_size, frontend_size, btof, flip_horizontal) for k, v in coords.items()}
        else:
            # Return non-coordinate values unchanged
            return coords

    def get_image_with_metadata(self):
        if self.viewmodel.states['active_side'] == 'ap':
            image_data = self.viewmodel.imgs[0]
        elif self.viewmodel.states['active_side'] == 'ob':
            image_data = self.viewmodel.imgs[1]

        if image_data['image'] is not None:
            image_base64 = self.viewmodel.encode(image_data['image'])
        
        # Convert metadata coordinates from backend to frontend scale
        converted_metadata = self.backend_to_frontend_coords(image_data['metadata'])

        return {
            'image': image_base64,
            'metadata': converted_metadata,
            'checkmark': image_data['checkmark'],
            'recon': image_data['recon'],
            'error': image_data['error'],
            'next': image_data['next'],
            'measurements': image_data['measurements'],
            'side': image_data['side'],
            'jump': image_data['jump'] if 'jump' in image_data else None
        }

    def update_landmarks(self, ui_l, ui_r, limgside, rimgside, stage):
        l = self.backend_to_frontend_coords(ui_l, btof = False) if ui_l else None
        # Apply horizontal flipping for right metadata
        r = self.backend_to_frontend_coords(ui_r, btof = False) if ui_r else None
        if stage == 0:
            if self.model.data['hp1-ap']['framedata']:
                self.model.data['hp1-ap']['framedata']['landmarks'] = l
            else:
                self.model.data['hp1-ap']['framedata']= {'landmarks': l}
            if self.model.data['hp1-ob']['framedata']:
                self.model.data['hp1-ob']['framedata']['landmarks'] = r
            else:
                self.model.data['hp1-ob']['framedata']= {'landmarks': r}
            
            if limgside:
                self.model.data['hp1-ap']['side'] = limgside
            if rimgside:
                self.model.data['hp1-ob']['side'] = rimgside
        
        if stage == 1:
            if self.model.data['hp2-ap']['framedata']:
                self.model.data['hp2-ap']['framedata']['landmarks'] = l
            else:
                self.model.data['hp2-ap']['framedata']= {'landmarks': l}
            if self.model.data['hp2-ob']['framedata']:
                self.model.data['hp2-ob']['framedata']['landmarks'] = r
            else:
                self.model.data['hp2-ob']['framedata']= {'landmarks': r}
            
            if limgside:
                self.model.data['hp2-ap']['side'] = limgside
            if rimgside:
                self.model.data['hp2-ob']['side'] = rimgside
        
        if stage == 2:
            if self.model.data['cup-ap']['framedata']:
                self.model.data['cup-ap']['framedata']['landmarks'] = l
            else:
                self.model.data['cup-ap']['framedata']= {'landmarks': l}
            if self.model.data['cup-ob']['framedata']:
                self.model.data['cup-ob']['framedata']['landmarks'] = r
            else:
                self.model.data['cup-ob']['framedata']= {'landmarks': r}
            
            if limgside:
                self.model.data['cup-ap']['side'] = limgside
            if rimgside:
                self.model.data['cup-ob']['side'] = rimgside
        
        if stage == 3:
            if self.model.data['tri-ap']['framedata']:
                self.model.data['tri-ap']['framedata']['landmarks'] = l
            else:
                self.model.data['tri-ap']['framedata']= {'landmarks': l}
            if self.model.data['tri-ob']['framedata']:
                self.model.data['tri-ob']['framedata']['landmarks'] = r
            else:
                self.model.data['tri-ob']['framedata']= {'landmarks': r}
            
            if limgside:
                self.model.data['tri-ap']['side'] = limgside
            if rimgside:
                self.model.data['tri-ob']['side'] = rimgside
        
        
        self.uistates = 'landmarks' if 'ap' not in self.scn else 'None'
        self.pause_states = None
        self.viewmodel.imgs[0]['metadata'] = l
        self.viewmodel.imgs[1]['metadata'] = r

        self.viewmodel.imgs[0]['checkmark'] = 1
        self.viewmodel.imgs[1]['checkmark'] = 1
        if limgside:
            self.viewmodel.imgs[0]['side'] = limgside
        if rimgside:
            self.viewmodel.imgs[1]['side'] = rimgside
        

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
        
        result = self.frame_grabber.connect(device)
        
        if result.get('connected', False):

            # Fetch the first frame
            frame = controller.frame_grabber.fetchFrame()
            
            if frame is not None:
                # Convert numpy array to JPEG
                retval, buffer = cv2.imencode('.jpg', frame)
                
                if retval:
                    # Convert to base64
                    jpg_bytes = buffer.tobytes()
                    base64_str = base64.b64encode(jpg_bytes).decode('utf-8')
                    
                    # Add the frame to the result as a data URI
                    result['frame'] = f"data:image/jpeg;base64,{base64_str}"
                else:
                    controller.logger.warning("Failed to encode frame to JPEG")
            else:
                controller.logger.warning("No frame available after connection")
        
        return result
        

    def set_ai_autocollect_modes(self, data):
        if 'ai_mode' in data:
            ai_mode = data.get('ai_mode', True)
            self.ai_mode = ai_mode
            self.model.ai_mode = ai_mode
        if 'autocollect' in data:
            autocollect = data.get('autocollect', True)
            self.autocollect = autocollect

    def next(self, state, stage):
        self.uistates = state
        self.viewmodel.states['stage'] = stage
        if self.imu: self.imu.confirm_save()

    def save_screen(self, stage, file):
        save_dir = f'{self.exam.exam_folder}/viewpairs'
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the file
        filename = f'screenshot{stage}.png'
        file_path = os.path.join(save_dir, filename)
        file.save(file_path)
        
        image = Image.open(file)
        image_array = np.array(image)
        self.model.viewpairs[stage] = image_array

    def get_screen(self, stage):
        global controller
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        
        vp = controller.model.viewpairs[stage]
        
        if vp is None:
            return {
            'img': None,
            }
        
        # Convert the image to base64 encoding
        image_base64 = self.viewmodel.encode(vp)
        # Return both image and metadata in JSON
        return {
            'img': f'data:image/jpeg;base64,{image_base64}',
        }

    def get_stitch(self, stage):
        if stage < 2:
            stitch = self.model.data['pelvis']['stitch']
        if stage == 2:
            stitch = self.model.data['regcup']['stitch']
        if stage == 3:
            stitch = self.model.data['regtri']['stitch']
        
        if stitch is None:
            return jsonify({
            'img': None,
            })
        
        # Convert the image to base64 encoding
        image_base64 = self.viewmodel.encode(stitch)
        
        # Return both image and metadata in JSON
        return jsonify({
            'img': f'data:image/jpeg;base64,{image_base64}',
        })


    def start_processing(self):
        """Start the frame processing loop in a separate thread."""
        if self.is_running:
            self.logger.warning("Processing is already running")
            return False
        
        self.is_running = True
        self.process_thread = threading.Thread(target=self._process_loop)
        self.process_thread.start()
        self.logger.info("Started image processing")
        return True

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
            if frame is not None: print (self.scn,self.uistates)
            newscn, uistates, action = self.model.eval_modelscnario(frame, self.scn, self.viewmodel.states['active_side'], self.uistates)
            if action is not None:
                match action[0]:
                    case 'copy_stage_data':
                        self.model.copy_stage_data(action[1], action[2])

                    case 'set_success_to_none':
                        self.model.copy_stage_data(action[1])

                    case 'set_cupreg':
                        self.imu.setcupreg()

            if newscn == self.scn or newscn[-3:] == 'end':
                continue
            self.uistates = uistates
            self.is_processing = True
            if self.tracking: 
                self.imu.handle_window_close(self.viewmodel.states['stage'])
                analysis_type, data_for_model, data_for_calib, data_for_exam = self.model.exec(newscn, frame, self.imu.tilt_angle, self.imu.rotation_angle)
            else: 
                analysis_type, data_for_model, data_for_calib, data_for_exam = self.model.exec(newscn, frame)
            
            self.is_processing = False
            # add handling of 'exception:'
            #if analysis_type == 'exception':
            #     
            print(data_for_model, newscn)
            self.scn = newscn[:-3] + 'end'
            self.model.update(analysis_type, data_for_model)
            self.viewmodel.update(analysis_type, data_for_model)
            #self.exam.save(analysis_type, data_for_exam, frame)

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
                    if self.model.data['hp1-ap']['image'] is not None and self.model.data['hp1-ob']['image'] is not None:
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
                if self.uistates == 'landmarks':
                    if self.model.data['hp2-ap']['image'] is not None and self.model.data['hp2-ob']['image'] is not None:
                        self.uistates = None
                        return 'rcn:hmplv2:bgn'

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
                        self.uistates = None
                        if self.viewmodel.states['active_side'] == 'ap':
                            self.scn = 'frm:cup-ap:end'
                        if self.viewmodel.states['active_side'] == 'ob':
                            self.scn = 'frm:cup-ob:end'
                        return self.scn
                    if self.uistates == 'skip':                        
                        self.uistates = None
                        if self.viewmodel.states['active_side'] == 'ap':
                            self.scn = 'frm:tri-ap:end'
                        if self.viewmodel.states['active_side'] == 'ob':
                            self.scn = 'frm:tri-ob:end'
                        return self.scn

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
                    self.model.data['tri-ap'] = {'image': None, 'metadata': None, 'success': False, 'side': None}
                    self.model.data['tri-ob'] = {'image': None, 'metadata': None, 'success': False, 'side': None}
                    self.model.data['tri-ap']['image'] = self.model.data['cup-ap']['image']
                    self.model.data['tri-ob']['image'] = self.model.data['cup-ob']['image']
                    self.scn = 'frm:tri-ap:end'
                    return self.scn
                if self.uistates == 'landmarks':
                    if self.model.data['cup-ap']['image'] is not None and self.model.data['cup-ob']['image'] is not None:
                        self.uistates = None
                        return 'rcn:acecup:bgn'

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
                    if self.tracking: self.imu.iscupreg = True

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
                    self.model.data['cup-ap'] = {'image': None, 'metadata': None, 'success': False, 'side': None}
                    self.model.data['cup-ob'] = {'image': None, 'metadata': None, 'success': False, 'side': None}
                    self.model.data['cup-ap']['image'] = self.model.data['tri-ap']['image']
                    self.model.data['cup-ob']['image'] = self.model.data['tri-ob']['image']
                    self.scn = 'frm:cup-ap:end'
                    return self.scn
                if self.uistates == 'landmarks':
                    if self.model.data['tri-ap']['image'] is not None and self.model.data['tri-ob']['image'] is not None:
                        self.uistates = None
                        return 'rcn:tothip:bgn'

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

                    
