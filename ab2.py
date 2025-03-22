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
        self.viewpairs = [None]*4
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
            'pelvis': {'stitch': None, 'success': False},

            'cup-ap': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'cup-ob': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'acecup': {'success': False},
            'regcup': {'stitch': None, 'success': False},

            'tri-ap': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'tri-ob': {'image': None, 'metadata': None, 'success': False, 'side': None},
            'tothip': {'success': False},
            'regtri': {'stitch': None, 'success': False}
        }
    def getfrmcase(self, c):
        match c:
            case 'hmplv1': return ['hp1-ap', 'hp1-ob']
            case 'hmplv2'| 'pelvis': return ['hp2-ap', 'hp2-ob']
            case 'acecup'| 'regcup': return ['cup-ap', 'cup-ob']
            case 'tothip'| 'regtri': return ['tri-ap', 'tri-ob']

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
            self.data[section]['success'] = None
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
            if section[:3] == 'hp2' or  section[:3] == 'tri':
                if side != self.data[section]['side']:
                    return {'metadata': None, 'checkmark': None, 'error': 'wrong side'}, frame
            self.is_processing = True

            # Load metadata
            file = 'hp1-ap-right.json' if section[-2:]=='ap' else 'hp2-ap-left.json'
            print(section[:-2])
            if section[:3] == 'cup':
                file = 'leftcup.json' if section[-2:]=='ap' else 'rightcup.json'
            if section[:3] == 'tri':
                file = 'lefttri.json' if section[-2:]=='ap' else 'righttri.json'
            with open(file, 'r') as f:
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
            self.data[section]['metadata'] = metadata
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
            self.data[section]['success'] = None
            curap = self.getfrmcase(section)[0]
            curob = self.getfrmcase(section)[1]
            if self.data[curap]['side'] != self.data[curob]['side']: 
                return {'checkmark': 3, 'error': 'recon fails, unmatched side'}, None
            self.is_processing = True
            metadata = {'ap': self.data[curap]['metadata'], 'ob': self.data[curob]['metadata']}
            
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
            if section == 'acecup':
                self.data['tri-ap']['side'] = self.data['cup-ap']['side']
                self.data['tri-ob']['side'] = self.data['tri-ap']['side']
            self.data[section]['success'] = True
            return result, None
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, None
        

    def reg(self, section):
        try:
            self.data[section]['success'] = None
            image = cv2.imread('./AP.png')
            curap = self.getfrmcase(section)[0]
            curob = self.getfrmcase(section)[1]
            difference = cv2.absdiff(image, self.data[curap]['image'])
            difference2 = cv2.absdiff(image, self.data[curob]['image'])
            if np.mean(difference) < 10 or np.mean(difference2) < 10:
                return {'error': 'reg fails'}, None
            self.is_processing = True
            res = self.stitch(self.data['hp1-ap']['image'],self.data[curap]['image'])
            result = {}
            if section != 'pelvis': result['measurements'] = 123
            self.is_processing = False

            self.data[section]['success'] = True
            self.data[section]['stitch'] = res
            return result, res
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
                        'folder': 'shots',
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
                        'folder': 'recons',
                        'type': 'hp1',
                        'metadata': data.get('metadata',None),
                        'timestamp': str(datetime.datetime.now())
                    }
                    
                    dataforvm = data
                    if 'metadata' in dataforvm:
                        dataforvm.pop('metadata')
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
                        'folder': 'shots',
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
                        'folder': 'recons',
                        'type': 'hp2',
                        'metadata': data.get('metadata',None),
                        'timestamp': str(datetime.datetime.now())
                    }
                    
                    dataforvm = data
                    dataforvm.pop('metadata')
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
                    dataforsave = {
                        'stitch': processed_frame,
                        'folder': 'regs',
                        'type': 'pelvis',
                        'measurements': data.get('measurements',None),
                        'timestamp': str(datetime.datetime.now())
                    }
                    
                    dataforvm = data 
                    if 'error' not in data: dataforvm['next'] = True

                    return dataforsave, dataforvm, None
                
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
                        'folder': 'shots',
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
                        'folder': 'recons',
                        'type': 'cup',
                        'metadata': data.get('metadata',None),
                        'timestamp': str(datetime.datetime.now())
                    }
                    
                    dataforvm = data
                    dataforvm.pop('metadata')
                    dataforvm['next'] = False

                    return dataforsave, dataforvm, processed_frame

                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'reg:regcup:bgn':
                try:
                    data, processed_frame = self.reg(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = {
                        'stitch': processed_frame,
                        'folder': 'regs',
                        'type': 'cuo',
                        'measurements': data.get('measurements',None),
                        'timestamp': str(datetime.datetime.now())
                    }
                    
                    dataforvm = data 
                    if 'error' not in data: dataforvm['next'] = True

                    return dataforsave, dataforvm, None
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )

            case 'frm:tri-ap:bgn' | 'frm:tri-ob:bgn':   
                try:
                    data, processed_frame = self.analyzeframe(scn[4:-4], frame)
                    
                    # Prepare data for different components
                    dataforsave = {
                        'folder': 'shots',
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
            case 'rcn:tothip:bgn':
                try:
                    data, processed_frame = self.reconstruct(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = {
                        'folder': 'recons',
                        'type': 'tri',
                        'metadata': data.get('metadata',None),
                        'timestamp': str(datetime.datetime.now())
                    }
                    
                    dataforvm = data
                    dataforvm.pop('metadata')
                    dataforvm['next'] = False

                    return dataforsave, dataforvm, processed_frame

                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case 'reg:regtri:bgn':
                try:
                    data, processed_frame = self.reg(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = {
                        'stitch': processed_frame,
                        'folder': 'regs',
                        'type': 'tri',
                        'measurements': data.get('measurements',None),
                        'timestamp': str(datetime.datetime.now())
                    }
                    
                    dataforvm = data 

                    return dataforsave, dataforvm, None
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            case _:
                return None, None, None
