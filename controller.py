import threading
import time
from typing import Optional
import numpy as np
from PIL import Image
import cv2
import os
from model import Model

from fg_handler import FrameGrabber_handler
from viewmodel import ViewModel
import json
from imu2 import IMU_handler
from exam import Exam
import base64

class Controller:
    def __init__(self, config = None, calib = None,  panel = None, logger = None):
        self.calib = calib
        self.config = config
        self.fg_handler = FrameGrabber_handler(calib, panel, self.config.get("testpanel_config", False).get("fg_simulation", False), logger)

        self.is_running = False
        self.process_thread = None
        self.lock = threading.Lock()
        
        self.panel = None
        # Initialize based on configuration
        self.on_simulation = self.config.get("testpanel_config", False).get("panel_on", False) 
        self.autocollect = self.config.get('framegrabber_autocollect', True)
        self.ai_mode = self.config.get("frame_prediction_config").get("ai_mode", True)
        self.is_processing = False
        self.active_side = None
        self.stage = 0
        self.scn = 'init'
        self.jumpped = False
        self.lockside = False
        #self.unexpected_error = None
        self.bugs = [None]

        self.model = Model(self.ai_mode, self.on_simulation, self.config, self.calib.get("frame_analysis_config"), self.calib.get("distortion", {}), self.calib.get("gantry", {}), self.bugs, logger)
        
        
        self.viewmodel = ViewModel(config, self.bugs, logger)
        self.exam = Exam(self.calib['folder'], self.bugs, logger)
        self.pause_states= None
        self.uistates = None
        self.do_capture = False
        self.check_interval = 0.1
        
        self.logger = logger
        self.imu_handler = None
        
        # Initialize IMU if enabled in config
        self.tracking = self.config.get('testpanel_config').get("imu_sim", True)
        if self.tracking: 
            self.imu_handler = IMU_handler(self.config.get("imu_device_config"), self.calib["imu_handler_config"]["apply_target"], self.calib["imu_handler_config"]["carm_range_tilt"], self.calib["imu_handler_config"]["carm_range_rotation"], self.calib["imu_handler_config"]["carm_target_tilt"], self.calib["imu_handler_config"]["carm_target_rotation"], tol = self.calib["imu_handler_config"]["stable_movement_tol"], sim = config.get('testpanel_config').get("imu_sim", False), panel = panel)

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
            cur_sensor = self.imu_handler.sensor
            self.imu_handler = IMU_handler(self.config.get("imu_device_config"), self.calib["imu_handler_config"]["apply_target"], self.calib["imu_handler_config"]["carm_range_tilt"], self.calib["imu_handler_config"]["carm_range_rotation"], self.calib["imu_handler_config"]["carm_target_tilt"], self.calib["imu_handler_config"]["carm_target_rotation"], tol = self.calib["imu_handler_config"]["stable_movement_tol"], sim = self.config.get('testpanel_config').get("imu_sim", False), panel = self.panel)
            cur_sensor.handler = self.imu_handler

    def get_controller_states(self):
        tmp = self.bugs[0] if self.bugs[0] else None
        self.bugs[0] = None
        return{
            'is_processing': self.is_processing,
            'ai_mode' : self.ai_mode,
            'autocollect': self.autocollect,
            'active_side': self.active_side,
            'stage': self.stage,
            'scn': self.scn,
            'tracking': self.tracking,
            'unexpected_error': tmp,
            'bugs': self.bugs[1:]
        }

    def get_states(self):
        self.viewmodel.update_state(self.get_controller_states())
        self.viewmodel.update_state({"C-arm Model": self.calib['carm_id'].get("name", None)})
        self.viewmodel.update_state(self.model.get_model_states())

        # Update video_on based on frame_grabber state
        self.viewmodel.update_state(self.fg_handler.get_fg_states())
        
        # Update imu_on based on IMU is_connected
        
        if self.tracking and not self.lockside:
            imu_states = self.imu_handler.get_all(self.stage, self.model.data)
            imu_states['imu_on'] = False if not hasattr(self, 'imu_handler') else getattr(self.imu_handler.sensor, 'is_connected', True)  
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

    def update_landmarks(self, ui_l, ui_r, limgside, rimgside, brightness, contrast, stage):
        l = self.backend_to_frontend_coords(ui_l, btof = False) if ui_l else None
        # Apply horizontal flipping for right metadata
        r = self.backend_to_frontend_coords(ui_r, btof = False) if ui_r else None
        stages = [['hp1-ap', 'hp1-ob'], ['hp2-ap', 'hp2-ob'], ['cup-ap', 'cup-ob'], ['tri-ap', 'tri-ob']]

        if self.model.data[stages[stage][0]]['framedata']:
            self.model.data[stages[stage][0]]['framedata']['landmarks'] = l
            self.model.data[stages[stage][0]]['framedata']['brightness'] = brightness[0]
            self.model.data[stages[stage][0]]['framedata']['contrast'] = contrast[0]
            self.model.data[stages[stage][0]]['framedata']['tb'] = self.model.update_landmarks(l)
        else:
            self.model.data[stages[stage][0]]['framedata'] = {'landmarks' : l, 'brightness' : brightness[0], 'contrast' : contrast[0], 'tb': self.model.update_landmarks(l)}

        if self.model.data[stages[stage][1]]['framedata']:
            self.model.data[stages[stage][1]]['framedata']['landmarks'] = r
            self.model.data[stages[stage][1]]['framedata']['brightness'] = brightness[1]
            self.model.data[stages[stage][1]]['framedata']['contrast'] = contrast[1]
            self.model.data[stages[stage][1]]['framedata']['tb'] = self.model.update_landmarks(r)
        else:
            self.model.data[stages[stage][1]]['framedata'] = {'landmarks' : l, 'brightness' : brightness[0], 'contrast' : contrast[0], 'tb': self.model.update_landmarks(r)}
   
        
        if l:
            self.model.data[stages[stage][0]]['success'] = True
        if r:
            self.model.data[stages[stage][1]]['success'] = True

        if limgside:
            self.model.data[stages[stage][0]]['side'] = limgside
        if rimgside:
            self.model.data[stages[stage][1]]['side'] = rimgside
        
        
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
        
        result = self.fg_handler.connect(device)
        time.sleep(1)
        if result.get('connected', False):

            # Fetch the first frame
            frame = self.fg_handler.fetchFrame()
            
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
        self.model.viewpairs[stage] = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

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
    
    def load(self):
        rt = []
        fl = ['template-l.json', 'template-r.json', 'cuptemplate-l.json', 'cuptemplate-r.json', 'tritemplate-l.json', 'tritemplate-r.json']
         
        for i in range(len(fl)):
            with open(f'./config/{self.config.get("frontend_config").get("templates_path")}/{fl[i]}', 'r') as f:
                tp = json.load(f)
                tp = tp['landmarks']
            with open(f'./config/{self.config.get("frontend_config").get("templates_path")}/landmarks {i}.json', 'r') as f:
                tb = json.load(f)
            self.model.default_templates.append(tp)
            self.model.default_tables.append(tb)
            metadata = self.model.update_ui_objects(tb, tp, red = True)
            rt.append(self.backend_to_frontend_coords(metadata))
        return rt

    def _process_loop(self):

        while self.is_running:
            try:
                if self.do_capture:
                    frame = self.fg_handler.last_frame
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
                                try:
                                    if self.tracking: self.imu_handler.set_cupreg(self.stage)
                                except Exception as e:
                                    self.bugs[0] = str(e)
                                    self.bugs.append(str(e))
                                    self.logger.error(self.bugs[0])

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
                    analysis_type, data_for_model, data_for_exam = self.model.exec(newscn, frame, self.imu_handler.tilt_angle, self.imu_handler.rotation_angle, self.imu_handler.tilttarget, self.imu_handler.act_rot)
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
            except Exception as e:
                self.is_processing = False
                self.is_running = False
                self.bugs[0] = str(e)
                self.bugs.append(str(e))
                self.logger.error(self.bugs[0])

    def update_backendstates(self):
        try:
            if not self.fg_handler._is_new_frame_available:
                return None
            f = self.fg_handler.fetchFrame()
            return f if not self.is_processing else None
        except Exception as e:
            self.bugs[0] = str(e)
            self.bugs.append(str(e))
            self.logger.error(self.bugs[0])
            return None


    def patient(self, data):
        self.model.patient_data = data
        self.exam.save_patient(data)

    def savepdf(self):
        images = [Image.fromarray(np.uint8(data)).convert('RGB') for data in self.model.viewpairs if data is not None]
        if not os.path.exists(self.config.get('report_config').get('report_save_path')):
            raise Exception('No path')
        pdf_path = f'{self.config.get('report_config').get('report_save_path')}/bbd1.pdf'
            
        images[0].save(
            pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
        )
