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
from imu import IMU_sensor
from imu2 import IMU_handler
from exam import Exam
import base64

class Controller:
    def __init__(self, config = None, calib = None,  panel = None):
        self.calib = calib
        self.config = config
        self.frame_grabber = FrameGrabber(panel, self.calib["FrameGrabber"], self.config.get("fg_simulation", False))

        self.is_running = False
        self.process_thread = None
        self.lock = threading.Lock()
        
        # Get configuration
        
        
        self.panel = None
        # Initialize based on configuration
        self.on_simulation = self.config.get("on_simulation", False) 
        self.autocollect = self.config.get('framegrabber_autocollect', True)
        self.ai_mode = self.config.get("ai_mode", True)
        self.is_processing = False
        self.active_side = None
        self.stage = 0
        self.scn = 'init'
        self.jumpped = False
        self.lockside = False

        self.model = Model(self.ai_mode, self.on_simulation, self.calib["Model"], self.calib["distortion"], self.calib["gantry"])
        
        
        self.viewmodel = ViewModel(config)
        self.exam = Exam(self.calib['folder'])
        self.pause_states= None
        self.uistates = None
        self.do_capture = False
        self.check_interval = 0.1
        
        self.logger = self.frame_grabber.logger
        self.imu_handler = None
        self.imu_sensor = None
        
        # Initialize IMU if enabled in config
        self.tracking = self.calib['IMU'].get("imu_on", True)
        if self.tracking: 
            self.imu_handler = IMU_handler(self.calib["IMU"]["ApplyTarget"], self.calib["IMU"]["CarmRangeTilt"], self.calib["IMU"]["CarmRangeRotation"], self.calib["IMU"]["CarmTargetTilt"], self.calib["IMU"]["CarmTargetRot"], tol = self.calib["IMU"]["tol"])
            self.imu_sensor = IMU_sensor(self.calib['IMU'].get("imu_port", "COM3"), self.imu_handler, panel, config.get("imu_simulation", False))

        if self.on_simulation:
            self.panel = panel
            self.panel.controller = self

    def restart(self):
        with self.lock:
            self.uistates = 'restart'
        self.model._resetdata()
        self.viewmodel.reset()
        self.scn = 'init'
        self.stage = 0
        if self.tracking:
            self.imu_handler = IMU_handler(self.calib["IMU"]["ApplyTarget"], self.calib["IMU"]["CarmRangeTilt"], self.calib["IMU"]["CarmRangeRotation"], self.calib["IMU"]["CarmTargetTilt"], self.calib["IMU"]["CarmTargetRot"], tol = self.calib["IMU"]["tol"])
            self.imu_sensor.handler = self.imu_handler

    def get_controller_states(self):
        return{
            'is_processing': self.is_processing,
            'ai_mode' : self.ai_mode,
            'autocollect': self.autocollect,
            'active_side': self.active_side,
            'stage': self.stage,
            'scn': self.scn,
            'tracking': self.tracking
        }

    def get_states(self):
        self.viewmodel.update_state(self.get_controller_states())
        self.viewmodel.update_state({"C-arm Model": self.calib['Carm'].get("C-arm Model", None)})
        self.viewmodel.update_state(self.model.get_model_states())

        # Update video_on based on frame_grabber state
        if hasattr(self, 'frame_grabber'):
            self.viewmodel.update_state(self.frame_grabber.get_fg_states())
        
        # Update imu_on based on IMU is_connected
        
        if self.tracking and not self.lockside:
            imu_states = self.imu_handler.get_all(self.stage)
            imu_states['imu_on'] = False if not hasattr(self, 'imu_sensor') else getattr(self.imu_sensor, 'is_connected', True)  # Default to True if property not found
            if not imu_states['imu_on']:
                imu_states['active_side'] = None
            self.active_side = imu_states['active_side'] 
            self.viewmodel.update_state(imu_states)
        
        return self.viewmodel.states
    
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
        image_data = self.viewmodel.imgs[1]
        if self.active_side == 'ap':
            image_data = self.viewmodel.imgs[0]

        if image_data['image'] is not None:
            image_base64 = self.viewmodel.encode(image_data['image'])
        
        # Convert metadata coordinates from backend to frontend scale
        converted_metadata = self.backend_to_frontend_coords(image_data['metadata'])
        self.lockside = False
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
            
            if l:
                self.model.data['hp1-ap']['success'] = True
            if r:
                self.model.data['hp1-ob']['success'] = True

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
            
            if l:
                self.model.data['hp2-ap']['success'] = True
            if r:
                self.model.data['hp2-ob']['success'] = True

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
            
            if l:
                self.model.data['cup-ap']['success'] = True
            if r:
                self.model.data['cup-ob']['success'] = True

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
            
            if l:
                self.model.data['tri-ap']['success'] = True
            if r:
                self.model.data['tri-ob']['success'] = True

            if limgside:
                self.model.data['tri-ap']['side'] = limgside
            if rimgside:
                self.model.data['tri-ob']['side'] = rimgside
        
        
        with self.lock:
            self.uistates = 'landmarks' 
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
        
        result = self.frame_grabber.connect(device)
        time.sleep(1)
        if result.get('connected', False):

            # Fetch the first frame
            frame = self.frame_grabber.fetchFrame()
            
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
                    self.logger.warning("Failed to encode frame to JPEG")
            else:
                self.logger.warning("No frame available after connection")
        
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
        with self.lock:
            self.uistates = state
        
        if self.imu_handler is not None: self.imu_handler.confirm_save(self.model.angles, self.stage)
        self.stage = stage

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
        vp = self.model.viewpairs[stage]
        
        if vp is None:
            return {
            'img': None,
            }
        
        # Convert the image to base64 encoding
        image_base64 = self.viewmodel.encode(vp)
        # Return both image and metadata in JSON
        return {
            'img': image_base64,
        }

    def get_stitch(self, stage):
        if stage < 2:
            stitch = self.model.data['pelvis']['stitch']
        if stage == 2:
            stitch = self.model.data['regcup']['stitch']
        if stage == 3:
            stitch = self.model.data['regtri']['stitch']
        
        if stitch is None:
            return {
            'img': None,
            }
        
        # Convert the image to base64 encoding
        image_base64 = self.viewmodel.encode(stitch)
        
        # Return both image and metadata in JSON
        return {
            'img': image_base64,
        }


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

            with self.lock:
                newscn, self.uistates, action = self.model.eval_modelscnario(frame, self.scn, self.active_side, self.uistates)
        
                if action is not None:
                    match action[0]:
                        case 'copy_stage_data':
                            self.model.copy_stage_data(action[1], action[2])

                        case 'set_success_to_none':
                            self.model.set_success_to_none(action[1])

                        case 'set_imu_setcupreg':
                            if self.tracking: self.imu_handler.set_cupreg()
                if self.jumpped:
                    self.jumpped = False
                    continue
                    
                if newscn == self.scn or newscn[-3:] != 'bgn':
                    self.scn = newscn
                    self.is_processing = False
                    continue

            self.is_processing = True
            self.lockside = True
            if self.tracking: 
                self.imu_handler.handle_window_close(self.stage)
                analysis_type, data_for_model, data_for_exam = self.model.exec(newscn, frame, self.imu_sensor.tilt_angle, self.imu_sensor.rotation_angle, self.imu_handler.tilttarget, self.imu_handler.act_rot)
            else: 
                analysis_type, data_for_model, data_for_exam = self.model.exec(newscn, frame)
            
            
            # add handling of 'exception:'
            #if analysis_type == 'exception':
            #     
            print(data_for_model, newscn)
            self.scn = newscn[:-3] + 'end'
            self.model.update(analysis_type, data_for_model)
            print(self.model.data)
            self.viewmodel.update(analysis_type, data_for_model)
            self.exam.save(analysis_type, data_for_exam, frame)

    def update_backendstates(self):
        if not self.frame_grabber._is_new_frame_available:
            return None
        f = self.frame_grabber.fetchFrame()
        return f if not self.is_processing else None

    def patient(self, data):
        self.model.patient_data = data
        self.exam.save_patient(data)

    def savepdf(self):
        images = [Image.fromarray(np.uint8(data)).convert('RGB') for data in self.model.viewpairs if data is not None]
        if not os.path.exists(self.config.get('pdf_path')):
            raise Exception('No path')
        pdf_path = f'{self.config.get('pdf_path')}bbd1.pdf'
            
        images[0].save(
            pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
        )
