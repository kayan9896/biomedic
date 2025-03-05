import cv2
import numpy as np
import time
import threading
import json
import datetime

class AnalyzeBox:
    def __init__(self):
        self.progress = 0
        self._lock = threading.Lock()
        self.images = [[None]*4, [None]*2, [None]*2]
        self.is_processing = False
        self._stitch_thread = None
        self.mode = 1  
        self.resetdata()

    def resetdata(self):
        self.data = {
            'hp1-ap': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'hp1-ob': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'hmplv1': {'success': False},
            'hp2-ap': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'hp2-ob': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'hmplv2': {'success': False},
            'pelvis': {'stich': None, 'success': False}
        }

    def stitch(self, frame1, frame2):
        """Stitch two frames together."""
        if frame1.shape[0] != frame2.shape[0]:
            max_height = max(frame1.shape[0], frame2.shape[0])
            frame1_resized = cv2.resize(frame1, (int(frame1.shape[1] * max_height / frame1.shape[0]), max_height))
            frame2_resized = cv2.resize(frame2, (int(frame2.shape[1] * max_height / frame2.shape[0]), max_height))
        else:
            frame1_resized, frame2_resized = frame1, frame2

        # Simulate processing with progress updates
        k=0
        for i in range(10000):
            for j in range(3000):
                with self._lock:
                    self.progress = (k + 1) /300000
                    k+=1

        # Stitch the images
        result = np.hstack((frame1_resized, frame2_resized))
        return result

    def analyzeframe(self, section, frame):
        try:
            image = cv2.imread('./glyph.png')
            difference = cv2.absdiff(image, frame)
            
            if np.mean(difference)<10:
                return {'metadata': None, 'checkmark': None, 'error': 'glyph'}, frame

            image2 = cv2.imread('./nomark.png')
            difference2 = cv2.absdiff(image2, frame)
            if np.mean(difference2)<10:
                return {'metadata': None, 'checkmark': 0, 'error': 'landmarks fail'}, frame

            image = cv2.imread('./l.png')
            difference = cv2.absdiff(image, frame)
            
            side = 'l' if np.mean(difference)<10 else 'r'
            if section[:3] == 'hp2' and side != self.data[section]['side']:
                return {'metadata': None, 'checkmark': None, 'error': 'wrong side'}, frame
            self.is_processing = True

            # Load metadata
            with open('metadata.json', 'r') as f:
                metadata = json.load(f)
            
            # Process frame and generate results
            result = {
                'metadata': metadata,
                'checkmark': 1,
                'error': None
            }
            
            k=0
            for i in range(10000):
                for j in range(3000):
                    with self._lock:
                        self.progress = (k + 1) /300000
                        k+=1
            self.is_processing = False

            self.data[section]['image'] = frame
            self.data[section]['meatdata'] = metadata
            self.data[section]['success'] = True
            self.data[section]['side'] = side
            return result, frame
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, None

    def reconstruct(self, section):
        try:
            if section == 'hmplv1':
                if self.data['hp1-ap']['side'] != self.data['hp1-ob']['side']: 
                    return {'checkmark': 3, 'error': 'recon fails, unmatched side'}, None
            self.is_processing = True
            # Load metadata
            with open('metadata.json', 'r') as f:
                metadata = json.load(f)
            
            # Process frame and generate results
            result = {
                'metadata': metadata,
                'checkmark': 2,
                'error': None
            }
            
            k=0
            for i in range(10000):
                for j in range(3000):
                    with self._lock:
                        self.progress = (k + 1) /300000
                        k+=1
            self.is_processing = False
            if section == 'hmplv1':
                self.data['hp2-ap']['side'] = 'l' if self.data['hp1-ap']['side'] == 'r' else 'r'
                self.data['hp2-ob']['side'] = self.data['hp2-ap']['side']
            self.data[section]['success'] = True
            return result, None
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, None

    def reg(self, section):
        try:
            image = cv2.imread('./AP.png')
            difference = cv2.absdiff(image, self.data['hp2-ap']['image'])
            difference2 = cv2.absdiff(image, self.data['hp2-ob']['image'])
            if np.mean(difference) < 10 or np.mean(difference2) < 10:
                return {'error': 'reg fails'}, None
            self.is_processing = True
            res = self.stitch(self.data['hp1-ap']['image'],self.data['hp2-ap']['image'])
            self.is_processing = False

            self.data[section]['success'] = True
            self.data[section]['stitch'] = res
            return {}, res
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, None

    def exec(self, scn, frame=None):
        match scn:
            case 'frm:hp1-ap:bgn' | 'frm:hp1-ob:bgn':   
                try:
                    data, processed_frame = self.analyzeframe(scn[4:-4], frame)
                    
                    # Prepare data for different components
                    dataforsave = {
                        'metadata': data['metadata']
                    }
                    
                    dataforvm = data
                    dataforvm['next'] = False
                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'rcn:hmplv1:bgn':
                try:
                    data, processed_frame = self.reconstruct(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = {
                        'type': 'hp1'
                    }
                    
                    dataforvm = data
                    if data['checkmark'] == 2:
                        dataforvm['next'] = True

                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    print(error)
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'frm:hp2-ap:bgn' | 'frm:hp2-ob:bgn':   
                try:
                    data, processed_frame = self.analyzeframe(scn[4:-4], frame)
                    
                    # Prepare data for different components
                    dataforsave = {
                        'metadata': data['metadata']
                    }
                    
                    dataforvm = data
                    dataforvm['next'] = False
                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'rcn:hmplv2:bgn':
                try:
                    data, processed_frame = self.reconstruct(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = {
                        'type': 'hp2'
                    }
                    
                    dataforvm = data
                    dataforvm['next'] = False

                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'reg:pelvis:bgn':
                try:
                    data, processed_frame = self.reg(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = {}
                    
                    dataforvm = data 
                    if 'error' not in data: dataforvm['next'] = True

                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'frm:cup-ap:bgn' | 'frm:cup-ob:bgn':   
                try:
                    data, processed_frame = self.analyzeframe(scn[4:-4], frame)
                    
                    # Prepare data for different components
                    dataforsave = {
                        'metadata': data['metadata']
                    }
                    
                    dataforvm = data
                    dataforvm['next'] = False
                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'rcn:acecup:bgn':
                try:
                    data, processed_frame = self.reconstruct(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = {
                        'type': 'cup'
                    }
                    
                    dataforvm = data
                    if data['checkmark'] == 2:
                        dataforvm['next'] = True

                    return dataforsave, dataforvm, processed_frame

                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case _:
                return None, None, None
