import cv2
import numpy as np
import time
import threading
import json
import datetime

class Model:
    def __init__(self):
        self.progress = 0
        self._lock = threading.Lock()
        self.viewpairs = [None]*4
        self.is_processing = False
        self._stitch_thread = None
        self.ai_mode = True
        self.on_simulation = False
        self.resetdata()
        self.test_data = {
            'ap': None, 
            'ob': None, 
            'recons': None, 
            'regs': None
        }

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

    def settest(self, testdata):
        self.test_data = testdata
    def analyzeframe(self, section, frame, tilt_angle=None, rotation_angle=None):
        try:
            self.data[section]['success'] = None
            
            self.is_processing = True
            section_type = section[-2:]  # ap, ob
            tmp = section[:-2] + 'ob'
            if section_type == 'ap': 
                self.data[tmp] = {'image': None, 'metadata': None, 'success': False, 'side': None}
                self.data[tmp]['side'] = self.data[section]['side']
            self.data[section]['image'] = frame
            
            if self.on_simulation:
                test_entry = self.test_data.get(section_type)
                if test_entry and test_entry.get('json_path'):
                    try:
                        error_code = test_entry['errors']
                        print(f"Simulating error {error_code} for {section}")
                        with open(test_entry['json_path'], 'r') as f:
                            metadata = json.load(f)
                        print(f"Using test data for {section}: {test_entry['file_name']}")
                    except Exception as e:
                        print(f"Error loading test JSON: {e}")
                        metadata = None
                else:
                    metadata = None
                
                # If no test metadata, use the default files
                if metadata is None:
                    file = 'hp1-ap-right.json' if side=='r' else 'hp2-ap-left.json'
                    if section[:3] == 'cup':
                        file = 'leftcup.json' if side=='l' else 'rightcup.json'
                    if section[:3] == 'tri':
                        file = 'lefttri.json' if side=='l' else 'righttri.json'
                    with open(file, 'r') as f:
                        metadata = json.load(f)
                
                metadata['imuangles'] = [tilt_angle, rotation_angle]

                side = metadata['side']
                if section[:3] == 'hp2' or  section[:3] == 'tri':
                    if side != self.data[section]['side']:
                        metadata['metadata'] = None
                        self.is_processing = False
                        return {'metadata': metadata, 'checkmark': None, 'recon': None, 'error': 'wrong side'}, frame
                

                if error_code == ['003']:
                    metadata['metadata'] = None
                    self.is_processing = False
                    return {'metadata': metadata, 'checkmark': None, 'recon': None, 'error': 'wrong side'}, frame

                if error_code == ['001']:
                    metadata['metadata'] = None
                    self.is_processing = False
                    return {'metadata': metadata, 'checkmark': None, 'recon': None, 'error': 'glyph'}, frame

                if error_code == ['002']:
                    metadata['metadata'] = None
                    self.is_processing = False
                    print(self.data)
                    return {'metadata': metadata, 'checkmark': 0, 'recon': None, 'error': 'landmarks fail', 'side': self.data[section]['side']}, frame

                if not self.ai_mode:
                    metadata['metadata'] = None
                    self.is_processing = False
                    self.data[section]['image'] = frame
                    self.data[section]['metadata'] = metadata
                    return {'metadata': metadata, 'checkmark': None, 'recon': None, 'error': None, 'side': self.data[section]['side']}, frame

                
                # Process frame and generate results
                result = {
                    'metadata': metadata,
                    'checkmark': 1,
                    'recon': None,
                    'side': side,
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
            #else: actual function

        except Exception as e:
            print(e)
            return {
                'success': False,
                'error': str(e)
            }, None

    def reconstruct(self, section):
        try:
            self.data[section]['success'] = None
            curap = self.getfrmcase(section)[0]
            curob = self.getfrmcase(section)[1]
            
            #self.is_processing = True
            if self.on_simulation:
                test_entry = self.test_data.get('recons')
                if test_entry and test_entry.get('json_path'):
                    try:
                        error_code = test_entry['errors']
                        print(f"Simulating error {error_code} for {section}")
                        with open(test_entry['json_path'], 'r') as f:
                            metadata = json.load(f)
                        print(f"Using test data for {section}: {test_entry['file_name']}")
                    except Exception as e:
                        print(f"Error loading test JSON: {e}")
                        metadata = None
                else:
                    metadata = None
                if self.data[curap]['side'] != self.data[curob]['side']: 
                    metadata['shot_1'] = None
                    metadata['shot_2'] = None
                    metadata['ReconResult'] = 'recon fails, unmatched side'
                    self.is_processing = False
                    return {'metadata': metadata, 'recon': 3, 'error': 'recon fails, unmatched side'}, None

                if error_code == ['004']: 
                    metadata['shot_1'] = None
                    metadata['shot_2'] = None
                    metadata['ReconResult'] = 'recon fails'
                    self.is_processing = False
                    return {'metadata': metadata, 'recon': 3, 'error': 'recon fails'}, None

                metadata['shot_1'] = self.data[curap]['metadata']
                metadata['shot_2'] = self.data[curob]['metadata']
                
                # Process frame and generate results
                result = {
                    'metadata': metadata,
                    'recon': 2,
                    'side': self.data[curap]['side'],
                    'error': None
                }
                

                self.is_processing = False
                if section == 'hmplv1':
                    self.data['hp2-ap']['side'] = 'l' if self.data['hp1-ap']['side'] == 'r' else 'r'
                    self.data['hp2-ob']['side'] = self.data['hp2-ap']['side']
                if section == 'acecup':
                    self.data['tri-ap']['side'] = self.data['cup-ap']['side']
                    self.data['tri-ob']['side'] = self.data['tri-ap']['side']
                self.data[section]['success'] = True
                self.data[section]['metadata'] = metadata
                return result, None
            #else: actual function

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, None
        

    def reg(self, section):
        try:
            self.data[section]['success'] = None
            curap = self.getfrmcase(section)[0]
            curob = self.getfrmcase(section)[1]

            self.is_processing = True

            if self.on_simulation:
                test_entry = self.test_data.get('regs')
                if test_entry and test_entry.get('json_path'):
                    try:
                        error_code = test_entry['errors']
                        print(f"Simulating error {error_code} for {section}")
                        with open(test_entry['json_path'], 'r') as f:
                            metadata = json.load(f)
                        print(f"Using test data for {section}: {test_entry['file_name']}")
                    except Exception as e:
                        print(f"Error loading test JSON: {e}")
                        metadata = None
                else:
                    metadata = None


                if error_code == ['005']:
                    metadata['Pelvis_Recon'] = None
                    metadata['Implant_Recon'] = None
                    metadata['RegsResult'] = 'reg fails'
                    self.is_processing = False
                    return metadata, None

                metadata['Pelvis_Recon'] = {'hmplv1':self.data['hmplv1']['metadata'], 'hmplv2':self.data['hmplv2']['metadata']}
                if section == 'regtri':
                    metadata['Implant_Recon'] = self.data['tothip']['metadata'] 
                if section == 'regcup':
                    metadata['Implant_Recon'] = self.data['acecup']['metadata'] 

                res = self.stitch(self.data['hp1-ap']['image'],self.data[curap]['image'])
                metadata['stitch'] = res
                
                self.is_processing = False

                self.data[section]['success'] = True
                self.data[section]['stitch'] = res
                return metadata, res
            #else: acutal function

        except Exception as e:
            print(e)
            return {
                'success': False,
                'error': str(e)
            }, None

    def exec(self, scn, frame=None, tilt_angle=None, rotation_angle=None):
        match scn:
            case 'frm:hp1-ap:bgn' | 'frm:hp1-ob:bgn' | 'frm:hp2-ap:bgn' | 'frm:hp2-ob:bgn' | 'frm:cup-ap:bgn' | 'frm:cup-ob:bgn' | 'frm:tri-ap:bgn' | 'frm:tri-ob:bgn':   
                try:
                    data, processed_frame = self.analyzeframe(scn[4:-4], frame, tilt_angle, rotation_angle)
                    
                    # Prepare data for different components
                    dataforsave = data['metadata']
                    
                    dataforvm = data
                    dataforvm['next'] = False

                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )

            case 'rcn:hmplv1:bgn' | 'rcn:hmplv2:bgn' | 'rcn:acecup:bgn' | 'rcn:tothip:bgn':
                try:
                    data, processed_frame = self.reconstruct(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = data['metadata']
                    
                    dataforvm = data
                    if 'metadata' in dataforvm:
                        dataforvm.pop('metadata')

                    return dataforsave, dataforvm, processed_frame
                
                except Exception as error:
                    
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
   
            
            case 'reg:pelvis:bgn' | 'reg:regcup:bgn' | 'reg:regtri:bgn':
                try:
                    data, processed_frame = self.reg(scn[4:-4])
                    
                    # Prepare data for different components
                    dataforsave = data
                    
                    dataforvm = {}
                    if data['RegsResult'] != 'reg fails': 
                        dataforvm['next'] = True
                        dataforvm['measurements'] = data['RegsResult']
                    else: 
                        dataforvm['next'] = False
                        dataforvm['error'] = data['RegsResult']
                    

                    return dataforsave, dataforvm, None
                
                except Exception as error:
                    return (
                        {'success': False, 'error': str(error)},
                        {'success': False, 'error': str(error)},
                        None
                    )
            
            

            case _:
                return None, None, None
