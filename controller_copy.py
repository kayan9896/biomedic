import threading
import time
from typing import Optional
import numpy as np
from PIL import Image
import cv2
import os

from exam import Exam
from confirmaphip_core.workflows.workflow_mock import WorkflowMock as Model

from fg_handler import FrameGrabber_handler
from viewmodel import ViewModel
import json
from imu2 import IMU_handler

import base64

class Controller:
    def __init__(self, config = None, calib = None,  panel = None, logger = None, cpfolder = None, scaffold = None, workflow = None, socket = None):
        self.calib = calib
        self.config = config
        self.fg_handler = FrameGrabber_handler(calib, panel, self.config.get("testpanel_config", False).get("fg_simulation", False), logger, self)

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

        self.model = Model(self.config, self.calib, cpfolder, self.bugs, logger, scaffold, workflow)
        self.socket = socket
        
        self.viewmodel = ViewModel(config, self.bugs, logger, socket)
        
        self.pause_states= None
        self.uistates = None
        self.do_capture = False
        self.check_interval = 0.1
        
        self.logger = logger
        
        # Initialize IMU if enabled in config
        self.tracking = self.config.get('testpanel_config').get("imu_sim", True)
        
        if self.on_simulation:
            self.panel = panel
            self.panel.controller = self

    def update_select(self, select, cpfolder):
        self.model.carm = select
        self.model.exam.set_folder(cpfolder)
        self.fg_handler.update_select(select)
        

    def get_states(self):

        self.viewmodel.update_state({"C-arm Model": self.calib['carm_id']})

        # Update video_on based on frame_grabber state
        self.viewmodel.update_state(self.fg_handler.get_fg_states())
        
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
        
        if isinstance(coords, (list, tuple)):
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
        image_data = self.viewmodel.imgs
        if image_data['image'] is not None:
            image_base64 = self.viewmodel.encode(image_data['image'])
        
        # Convert metadata coordinates from backend to frontend scale
        converted_metadata = self.backend_to_frontend_coords(image_data['metadata'])
        self.lockside = False
        return {
            'image': image_base64,
            'metadata': converted_metadata,
            'pos': image_data['pos'],
            'error': image_data['error'],
        }


    def update_landmarks(self, ui_l, ui_r, limgside, rimgside, brightness, contrast, stage):
        pass
        

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
            frame = self.fg_handler.last_frame
            
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
            
        

    def run2(self, frame):
        self.processing = True

        frame_object = self.model.analyzeframe(frame) 
        err = frame_object.annotations['default'].error_code
        
        self.viewmodel.update('frame', frame_object, err)
        
        if not err:
            f_run, required_view, required_bm = self.model.next_analysis()
            while f_run:
                if required_view is not None:
                    bmodel = self.model.reconstruct(f_run, required_view, required_bm)
                else:
                    bmodel = self.model.reg(f_run, required_bm)
                self.viewmodel.update('report', bmodel, err)
                

                f_run, required_view, required_bm = self.model.next_analysis()


        self.processing = False
            


