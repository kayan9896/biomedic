from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np
import cv2
import base64

class ViewModel:
    def __init__(self, calib = None):
        self.states = {
            'ai_mode': 0,
            'tilt_angle': 0,
            'rotation_angle': 0,
            'img_count': 0,  
            'active_side': None,
            'is_processing': False,
            'progress': 0,
            'imu_on': True,
            'video_on':True,
            'stage': 0,

        }
        self.imgs = [{'image': None, 'metadata': None, 'checkmark': None, 'recon': None, 'error': None, 'next': False, 'measurements': None, 'side': None} for i in range(2)]

    def update(self, analysis_type, data_for_model):
        # Assuming dataforvm contains metadata
        image = None
        dataforvm = {}
        if analysis_type == 'frame':
            if data_for_model['analysis_error_code'] is None:
                image = data_for_model['processed_frame']
                dataforvm['metadata'] = data_for_model['landmarks']
                dataforvm['checkmark'] = 1
                dataforvm['recon'] = None
                dataforvm['error'] = None
                dataforvm['measurements'] = None
                dataforvm['next'] = False
                dataforvm['side'] = data_for_model['side']
            if data_for_model['analysis_error_code'] == '110':
                image = data_for_model['processed_frame']
                dataforvm['metadata'] = None
                dataforvm['checkmark'] = None
                dataforvm['recon'] = None
                dataforvm['error'] = '110'
                dataforvm['measurements'] = None
                dataforvm['next'] = False
                dataforvm['side'] = data_for_model['side']
            if data_for_model['analysis_error_code'] in {'111', '112'}:
                image = data_for_model['processed_frame']
                dataforvm['error'] = 'glyph' if data_for_model['analysis_error_code'] == '111' else 'ref'
            if data_for_model['analysis_error_code'] == '113':
                image = data_for_model['processed_frame']
                dataforvm['metadata'] = None
                dataforvm['checkmark'] = 0
                dataforvm['recon'] = None
                dataforvm['error'] = '113'
                dataforvm['measurements'] = None
                dataforvm['next'] = False
                dataforvm['side'] = data_for_model['side']

        if analysis_type == 'recon':
            if data_for_model['analysis_error_code'] is None:
                dataforvm['recon'] = 2
                dataforvm['error'] = None
                dataforvm['measurements'] = None
                dataforvm['next'] = True if self.states['stage'] == 0 else False
            if data_for_model['analysis_error_code'] == '120':
                dataforvm['recon'] = 3
                dataforvm['error'] = 'recon fails'
                dataforvm['measurements'] = None
                dataforvm['next'] = False

        if analysis_type == 'reg':
            if data_for_model['analysis_error_code'] is None:
                dataforvm['recon'] = 2
                dataforvm['error'] = None
                dataforvm['measurements'] = data_for_model['measurements']
                dataforvm['next'] = True 
            if data_for_model['analysis_error_code'] == '130':
                dataforvm['recon'] = 2
                dataforvm['error'] = 'reg fails'
                dataforvm['measurements'] = None
                dataforvm['next'] = False
        
        if self.states['active_side'] == 'ap':
            if image is not None: self.imgs[0]['image'] = image
            if 'jump' in self.imgs[0]: self.imgs[0].pop('jump')
            for i in dataforvm:
                self.imgs[0][i] = dataforvm[i]
            self.imgs[1]['recon'] = self.imgs[0]['recon']
        elif self.states['active_side'] == 'ob':
            if image is not None: self.imgs[1]['image'] = image
            if 'jump' in self.imgs[1]: self.imgs[1].pop('jump')
            for i in dataforvm:
                self.imgs[1][i] = dataforvm[i]
            self.imgs[0]['recon'] = self.imgs[1]['recon']
        
        self.update_img_count()

    def update_img_count(self):
        """Update img_count cycling from 0 to 4"""
        current_count = self.states['img_count']
        self.states['img_count'] = (current_count + 1) % 5
    
    def encode(self, image):
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return f'data:image/jpeg;base64,{image_base64}'

    def jump(self, stage, data):
        testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
        blank_image = np.zeros((1, 1, 3), np.uint8)
        self.imgs[0]['image'], self.imgs[1]['image'] = blank_image, blank_image
        if stage == 0 or stage == 2 or stage == 4:
            testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
            jump = {'stage': stage//2, 'apimage': 'default', 'obimage': 'default', 'checkmark': None, 'recon': None, 'next': None, 'testmeas': testmeas, 'side': 'l' if data['hp1-ap']['side'] == 'r' else 'l' if stage == 2 else None}
        if stage == 1:
            testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
            apimage, obimage = data['hp1-ap']['image'], data['hp1-ob']['image']
            self.imgs[0]['image'], self.imgs[1]['image'] = apimage, obimage
            jump = {'stage': 0, 'apimage': self.encode(apimage), 'obimage': self.encode(obimage), 
            'apmetadata': data['hp1-ap']['metadata']['metadata'], 'obmetadata': data['hp1-ob']['metadata']['metadata'], 'side': data['hp1-ap']['side'],
            'checkmark': 1, 'recon': 2, 'next': True, 'testmeas': testmeas}
        if stage == 3:
            testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
            apimage, obimage = data['hp2-ap']['image'], data['hp2-ob']['image']
            self.imgs[0]['image'], self.imgs[1]['image'] = apimage, obimage
            jump = {'stage': 1, 'apimage': self.encode(apimage), 'obimage': self.encode(obimage), 
            'apmetadata': data['hp2-ap']['metadata']['metadata'], 'obmetadata': data['hp2-ob']['metadata']['metadata'], 'side': data['hp2-ap']['side'],
            'checkmark': 1, 'recon': 2, 'next': True, 'testmeas': testmeas}
        if stage == 5:
            testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
            testmeas.update(data['regcup']['metadata']['RegsResult'])
            apimage, obimage = data['cup-ap']['image'], data['cup-ob']['image']
            self.imgs[0]['image'], self.imgs[1]['image'] = apimage, obimage
            jump = {'stage': 2, 'apimage': self.encode(apimage), 'obimage': self.encode(obimage), 
            'apmetadata': data['cup-ap']['metadata']['metadata'], 'obmetadata': data['cup-ob']['metadata']['metadata'], 'side': data['cup-ap']['side'],
            'measurements': data['regcup']['metadata']['RegsResult'], 'testmeas': testmeas,
            'checkmark': 1, 'recon': 2, 'next': True}
        if stage == 6:
            testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
            testmeas.update(data['regcup']['metadata']['RegsResult'])
            jump = {'stage': stage//2, 'apimage': 'default', 'obimage': 'default', 'checkmark': None, 'side': data['cup-ap']['side'], 'recon': None, 'next': True, 'testmeas': testmeas, 'side': data['cup-ap']['side']}
        if stage == 7:
            testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
            jump = {'stage': stage//2, 'apimage': 'default', 'obimage': 'default', 'checkmark': None, 'recon': None, 'next': None, 'testmeas': testmeas, 'side': None}
        if stage == 8:
            testmeas = {'Inclination' : '-', 'Anteversion' : '-', 'LLD': '-mm', 'Offset': '-mm'}
            testmeas.update(data['regcup']['metadata']['RegsResult'])
            testmeas.update(data['regtri']['metadata']['RegsResult'])
            apimage, obimage = data['tri-ap']['image'], data['tri-ob']['image']
            self.imgs[0]['image'], self.imgs[1]['image'] = apimage, obimage
            jump = {'stage': 3, 'apimage': self.encode(apimage), 'obimage': self.encode(obimage), 
            'apmetadata': data['tri-ap']['metadata']['metadata'], 'obmetadata': data['tri-ob']['metadata']['metadata'], 'side': data['tri-ap']['side'],
            'measurements': data['regtri']['metadata']['RegsResult'], 'testmeas': testmeas,
            'checkmark': 1, 'recon': 2, 'next': 4}

        self.imgs[0]['jump'], self.imgs[1]['jump'] = jump, jump
        
        self.update_img_count()

    def update_state(self, key: str, value: any):
        """Update a specific state value"""
        self.states[key] = value

    def get_states(self):
        """Get all states"""
        return self.states
    


    