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
        self._result = None
        self.images = [[None]*4, [None]*2, [None]*2]
        self.stitched_result = [None]*2
        self.is_processing = False
        self._stitch_thread = None
        self.mode = 1  
        self.data={
            'hp1-ap': {'image': None, 'metadata': None, 'success': False},
            'hp1-ob': {'image': None, 'metadata': None, 'success': False},
            'hmplv1': {'success': False}
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
        self._result = np.hstack((frame1_resized, frame2_resized))
        return self._result

    def analyzeframe(self, scn, frame):
        try:
            self.is_processing = True
            # Load metadata
            with open('metadata.json', 'r') as f:
                metadata = json.load(f)
            
            # Process frame and generate results
            result = {
                'metadata': metadata
            }
            
            k=0
            for i in range(10000):
                for j in range(3000):
                    with self._lock:
                        self.progress = (k + 1) /300000
                        k+=1
            self.is_processing = False
            i = scn[4:-4]
            print(i)
            self.data[i]['meatdata'] = metadata
            self.data[i]['success'] = True
            return result, frame
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, None

    def reconstruct(self, scn):
        try:
            self.is_processing = True
            # Load metadata
            with open('metadata.json', 'r') as f:
                metadata = json.load(f)
            
            # Process frame and generate results
            result = {
                'metadata': metadata
            }
            
            k=0
            for i in range(10000):
                for j in range(3000):
                    with self._lock:
                        self.progress = (k + 1) /300000
                        k+=1
            self.is_processing = False
            i = scn[4:-4]
            self.data[i]['success'] = True
            return result, None
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, None
    
    def exec(self, scn, frame=None):
        match scn:
            case 'frm:hp1-ap:bgn' | 'frm:hp1-ob:bgn':   
                try:
                    data, processed_frame = self.analyzeframe(scn, frame)
                    
                    # Prepare data for different components
                    dataforsave = {
                        'metadata': data['metadata']
                    }
                    
                    dataforvm = {
                        'metadata': data['metadata']
                    }
                    
                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'rcn:hmplv1:bgn':
                try:
                    data, processed_frame = self.reconstruct(scn)
                    
                    # Prepare data for different components
                    dataforsave = {
                        'type': 'hp1',
                        'metadata': data['metadata']
                    }
                    
                    dataforvm = {
                        'metadata': data['metadata']
                    }
                    
                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case _:
                return None, None, None
