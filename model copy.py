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
        self.calib = None
        self.distortion = None
        self.gantry = None

        self.test_data = None

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
        self.viewpairs = [None]*4

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
        print(testdata)

    def filldata(self, stage):
        self.resetdata()
        if stage >= 1:
            hp1apimage = cv2.imread(self.test_data['hp1']['ap']['image_path'])
            with open(self.test_data['hp1']['ap']['json_path'], 'r') as f:
                hp1apdata = json.load(f)
            self.data['hp1-ap'] = {'image': hp1apimage, 'metadata': hp1apdata, 'success': True, 'side': hp1apdata['side']}
            hp1obimage = cv2.imread(self.test_data['hp1']['ob']['image_path'])
            with open(self.test_data['hp1']['ob']['json_path'], 'r') as f:
                hp1obdata = json.load(f)
            self.data['hp1-ob'] = {'image': hp1obimage, 'metadata': hp1obdata, 'success': True, 'side': hp1obdata['side']}
            with open(self.test_data['hp1']['recons']['json_path'], 'r') as f:
                hmplv1 = json.load(f)
            self.data['hmplv1'] = {'success': True, 'metadata': hmplv1}
            vp0 = cv2.imread(f'{self.test_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot0.png')
            self.viewpairs[0] = vp0
        if stage >= 3:
            hp2apimage = cv2.imread(self.test_data['hp2']['ap']['image_path'])
            with open(self.test_data['hp2']['ap']['json_path'], 'r') as f:
                hp2apdata = json.load(f)
            self.data['hp2-ap'] = {'image': hp2apimage, 'metadata': hp2apdata, 'success': True, 'side': hp2apdata['side']}
            hp2obimage = cv2.imread(self.test_data['hp2']['ob']['image_path'])
            with open(self.test_data['hp2']['ob']['json_path'], 'r') as f:
                hp2obdata = json.load(f)
            self.data['hp2-ob'] = {'image': hp2obimage, 'metadata': hp2obdata, 'success': True, 'side': hp2obdata['side']}
            with open(self.test_data['hp2']['recons']['json_path'], 'r') as f:
                hmplv2 = json.load(f)
            self.data['hmplv2'] = {'success': True, 'metadata': hmplv2}
            stitch = cv2.imread(f'{self.test_data['hp2']['regs']['json_path'][:-4]}png')
            self.data['pelvis'] = {'success': True, 'stitch': stitch}
            vp1 = cv2.imread(f'{self.test_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot1.png')
            self.viewpairs[1] = vp1
        if stage >= 5 and stage != 7:
            cupapimage = cv2.imread(self.test_data['cup']['ap']['image_path'])
            with open(self.test_data['cup']['ap']['json_path'], 'r') as f:
                cupapdata = json.load(f)
            self.data['cup-ap'] = {'image': cupapimage, 'metadata': cupapdata, 'success': True, 'side': cupapdata['side']}
            cupobimage = cv2.imread(self.test_data['cup']['ob']['image_path'])
            with open(self.test_data['cup']['ob']['json_path'], 'r') as f:
                cupobdata = json.load(f)
            self.data['cup-ob'] = {'image': cupobimage, 'metadata': cupobdata, 'success': True, 'side': cupobdata['side']}
            with open(self.test_data['cup']['recons']['json_path'], 'r') as f:
                acecup = json.load(f)
            self.data['acecup'] = {'success': True, 'metadata': acecup}
            stitch = cv2.imread(f'{self.test_data['cup']['regs']['json_path'][:-4]}png')
            with open(self.test_data['cup']['regs']['json_path'], 'r') as f:
                cupdata = json.load(f)
            self.data['regcup'] = {'success': True, 'stitch': stitch, 'metadata': cupdata}
            vp2 = cv2.imread(f'{self.test_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot2.png')
            self.viewpairs[2] = vp2
        if stage == 8:
            triapimage = cv2.imread(self.test_data['tri']['ap']['image_path'])
            with open(self.test_data['tri']['ap']['json_path'], 'r') as f:
                triapdata = json.load(f)
            self.data['tri-ap'] = {'image': triapimage, 'metadata': triapdata, 'success': True, 'side': triapdata['side']}
            triobimage = cv2.imread(self.test_data['tri']['ob']['image_path'])
            with open(self.test_data['tri']['ob']['json_path'], 'r') as f:
                triobdata = json.load(f)
            self.data['tri-ob'] = {'image': triobimage, 'metadata': triobdata, 'success': True, 'side': triobdata['side']}
            with open(self.test_data['tri']['recons']['json_path'], 'r') as f:
                acetri = json.load(f)
            self.data['acecup'] = {'success': True, 'metadata': acetri}
            stitch = cv2.imread(f'{self.test_data['tri']['regs']['json_path'][:-4]}png')
            with open(self.test_data['tri']['regs']['json_path'], 'r') as f:
                tridata = json.load(f)
            self.data['regtri'] = {'success': True, 'stitch': stitch, 'metadata': tridata}
            vp3 = cv2.imread(f'{self.test_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot2.png')
            self.viewpairs[3] = vp3


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
                test_entry = self.test_data.get(section[:-3]).get(section_type)
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
                self.distortion.update({(5,20): {'data': {}}})
                self.gantry.update({(1.5,0.2): {'data': {}}})
                metadata['distortion'] = self.distortion
                metadata['gantry'] = self.gantry

                side = metadata['side']
                if section[:3] == 'hp2' or (self.data['regcup'] and section[:3] == 'tri'):
                    if self.data[section]['side'] != None and side != self.data[section]['side']:
                        metadata['metadata'] = None
                        self.is_processing = False
                        return {'metadata': metadata, 'checkmark': None, 'recon': None, 'error': 'wrong side'}, frame
                

                if error_code == '110':
                    metadata['metadata'] = None
                    self.is_processing = False
                    return {'metadata': metadata, 'checkmark': None, 'recon': None, 'error': 'wrong side'}, frame

                if error_code == '111':
                    metadata['metadata'] = None
                    self.is_processing = False
                    return {'metadata': metadata, 'checkmark': None, 'error': 'glyph'}, frame

                if error_code == '112':
                    metadata['metadata'] = None
                    self.is_processing = False
                    return {'metadata': metadata, 'checkmark': None, 'error': 'ref'}, frame

                if error_code == '113':
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
                test_entry = self.test_data.get(curap[:-3]).get('recons')
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

                if error_code == '120': 
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
                test_entry = self.test_data.get(curap[:-3]).get('regs')
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


                if error_code == '130':
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
                    if data['recon'] == 2 and scn == 'rcn:hmplv1:bgn': 
                        dataforvm['next'] = True

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
