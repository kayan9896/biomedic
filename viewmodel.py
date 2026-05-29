from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np
import cv2
import base64

class ViewModel:
    def __init__(self, calib = None,  bugs = None, logger = None, socket = None):
        self.socket = socket

        self.setup = {
            'carm_model' : {},
            'carm_img' : None,
            'carm_status': False,
            'is_connected': False,
            'first_frame' : None,
            'selectedCArm': None,
            'currentStep': 1,
            'loading': False
        }

        self.preop = {
            'img_left_1' : None,
            'img_left_2' : None,
            'img_right_1' : None,
            'img_right_2' : None,
            'is_left_recon' : False,
            'is_right_recon' : False,
            'is_pelvis_recon' : False,
            'img_stitch' : None,
            'measure_lld' : None,
            'measure_offset' : None,
            'landmarks' : {},
            'next_enable': False
        }

        self.cup ={
            'img_pelvis' : None,
            'img_ap' : [None],
            'img_stitch' : None,
            'measure_anteversion' : None,
            'measure_inclination' : None,
            'landmarks' : {},
            'next_enable' : False,
        }

        self.tri = {
            'img_left_1' : None,
            'img_left_2' : None,
            'img_right_1' : None,
            'img_right_2' : None,
            'is_left_recon' : False,
            'is_right_recon' : False,
            'is_pelvis_recon' : False,
            'img_stitch' : None,
            'measure_lld' : None,
            'measure_offset' : None,
            'landmarks' : {},
            'next_enable': False
        }

        self.error = None
        self.pos = 0

    def update_setup(self, dic):
        self.setup.update(dic)
        self.socket.emit("setup", self.setup)


    def update(self, analysis_type, data_for_model, err):
        try:
            # Assuming dataforvm contains metadata
            
            if self.pos == 0:
                img = self.encode(data_for_model.image)
                self.preop['img_left_1'] = img
                self.socket.emit("preop", self.preop)
            if self.pos == 1:
                img = self.encode(data_for_model.image)
                self.preop['img_left_2'] = img
                self.socket.emit("preop", self.preop)
            if self.pos == 2:
                self.preop['is_left_recon'] = True
                self.socket.emit("preop", self.preop)
            if self.pos == 3:
                img = self.encode(data_for_model.image)
                self.preop['img_right_1'] = img
                self.socket.emit("preop", self.preop)
            if self.pos == 4:
                img = self.encode(data_for_model.image)
                self.preop['img_right_2'] = img
                self.socket.emit("preop", self.preop)
            if self.pos == 5:
                self.preop['is_right_recon'] = True
                self.socket.emit("preop", self.preop)
            if self.pos == 6:
                self.preop['is_pelvis_recon'] = True
                self.preop['img_stitch'] = self.preop['img_right_2']
                self.preop['measure_lld'] = '2cm'
                self.preop['next_enable'] = True
                self.socket.emit("preop", self.preop)
            if self.pos == 7:
                img = self.encode(data_for_model.image)
                self.cup['img_pelvis'] = img
                self.socket.emit("cup", self.cup)
                
            self.pos += 1

            
            
        except Exception as e:
            self.bugs[0] = str(e)
            self.logger.error(f'Exception in {self.__class__.__name__}: {str(e)}')
            self.bugs.append(str(e))

    
    def encode(self, image):
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return f'data:image/jpeg;base64,{image_base64}'

    def update_state(self, value):
        """Update a specific state value"""
        self.states.update(value)

    def get_states(self):
        """Get all states"""
        return self.states
    

    