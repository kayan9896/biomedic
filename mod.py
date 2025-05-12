from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np
import cv2

class ProcessingModel:
    def __init__(self, config = None):
        self.states = {
            'ai_mode': config.get("mode", 0),
            'angle': 0,
            'rotation_angle': 0,
            'img_count': 0,  
            'active_side': None,
            'is_processing': False,
            'progress': 0,
            'imu_on': True,
            'video_on':True,
            'stage': 0,
            "ap_rotation_angle": None,
            "ob_rotation_angle": None,
            "ob_rotation_angle2": None,
            "target_tilt_angle": None,
        }
        self.imgs = [{'image': None, 'metadata': None, 'checkmark': None, 'recon': None, 'error': None, 'next': False, 'measurements': None, 'side': None} for i in range(2)]

    def update(self, dataforvm, image):
        # Assuming dataforvm contains metadata
        
        if self.states['active_side'] == 'ap':
            self.imgs[0]['error'] = None
            self.imgs[0]['measurements'] = None
            if image is not None: self.imgs[0]['image'] = image
            for i in dataforvm:
                self.imgs[0][i] = dataforvm[i]
        elif self.states['active_side'] == 'ob':
            self.imgs[1]['error'] = None
            self.imgs[1]['measurements'] = None
            if image is not None: self.imgs[1]['image'] = image
            for i in dataforvm:
                self.imgs[1][i] = dataforvm[i]
        
        self.update_img_count()

    def update_img_count(self):
        """Update img_count cycling from 0 to 4"""
        current_count = self.states['img_count']
        self.states['img_count'] = (current_count + 1) % 5

    def update_state(self, key: str, value: any):
        """Update a specific state value"""
        self.states[key] = value

    def get_states(self):
        """Get all states"""
        return self.states
    


    