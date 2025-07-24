import cv2
import numpy as np
import time
import threading
import json
import datetime

class Frm:
    def __init__(self):
        self.rcn = None
        self.ap = None
        self.ob = None
        self.next_ap = None
        self.next_ob = None
        self.prev_ap = None
        self.prev_ob = None

class Rcn:
    def __init__(self):
        self.rcn = None
        self.reg = None
        self.ap = None
        self.ob = None

class Reg:
    def __init__(self):
        self.reg = None
        self.rcn = None
        self.ap = None
        self.ob = None
        self.next_ap = None
        self.next_ob = None

class Model:
    def __init__(self, ai_mode = True, on_simulation = False, calib = None, distortion = None , gantry = None):

        self.calib = None
        if calib is not None:
            self.extract_distortion = calib["ExtractDistortion"]
            self.correct_distortion = calib["CorrectDistortion"]
            self.extract_glyph = calib["ExtractGlyph"]
            self.extract_tracking = calib["ExtractTracking"]
            self.extract_camcalib = calib["ExtractCameraCalib"]
            self.calib={}
            self.calib['pixel_scale'] = calib["PixelScale"]
            self.calib['distortion'] = distortion
            self.calib['gantry'] = gantry


        self.ai_mode = ai_mode
        self.on_simulation = on_simulation

        self.progress = 0

        self.viewpairs = [None]*4

        self.data = None
        self._resetdata()
        self.sim_data = None
        self.patient_data = None

        self._lock = threading.Lock()
        self._stitch_thread = None
        # wait in seconds: use this values for waiting in seconds during analysis
        self._sim_wait_values ={
            'frame_analysis': 2,
            'recon': 2,
            'reg': 2
        }


    def _resetdata(self):
        self.viewpairs = [None]*4
        self.data = {
            'hp1-ap': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'hp1-ob': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'hmplv1': {'success': False, 'metadata': None, 'error_code': None},

            'hp2-ap': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'hp2-ob': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'hmplv2': {'success': False, 'metadata': None, 'error_code': None},
            'pelvis': {'stitch': None, 'success': False, 'metadata': None, 'error_code': None},

            'cup-ap': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'cup-ob': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'acecup': {'success': False, 'metadata': None, 'error_code': None},
            'regcup': {'stitch': None, 'success': False, 'metadata': None, 'error_code': None},

            'tri-ap': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'tri-ob': {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None},
            'tothip': {'success': False, 'metadata': None, 'error_code': None},
            'regtri': {'stitch': None, 'success': False, 'metadata': None, 'error_code': None}
        }

    def filldata(self, stage):
        self._resetdata()
        if stage >= 1:
            hp1apimage = cv2.imread(self.sim_data['hp1']['ap']['image_path'])
            with open(self.sim_data['hp1']['ap']['json_path'], 'r') as f:
                hp1apdata = json.load(f)
            self.data['hp1-ap'] = {'image': hp1apimage, 'framedata': hp1apdata, 'success': True, 'side': hp1apdata['side']}
            hp1obimage = cv2.imread(self.sim_data['hp1']['ob']['image_path'])
            with open(self.sim_data['hp1']['ob']['json_path'], 'r') as f:
                hp1obdata = json.load(f)
            self.data['hp1-ob'] = {'image': hp1obimage, 'framedata': hp1obdata, 'success': True, 'side': hp1obdata['side']}
            with open(self.sim_data['hp1']['recons']['json_path'], 'r') as f:
                hmplv1 = json.load(f)
            self.data['hmplv1'] = {'success': True, 'metadata': hmplv1}
            vp0 = cv2.imread(f'{self.sim_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot0.png')
            self.viewpairs[0] = vp0
        if stage >= 3:
            hp2apimage = cv2.imread(self.sim_data['hp2']['ap']['image_path'])
            with open(self.sim_data['hp2']['ap']['json_path'], 'r') as f:
                hp2apdata = json.load(f)
            self.data['hp2-ap'] = {'image': hp2apimage, 'framedata': hp2apdata, 'success': True, 'side': hp2apdata['side']}
            hp2obimage = cv2.imread(self.sim_data['hp2']['ob']['image_path'])
            with open(self.sim_data['hp2']['ob']['json_path'], 'r') as f:
                hp2obdata = json.load(f)
            self.data['hp2-ob'] = {'image': hp2obimage, 'framedata': hp2obdata, 'success': True, 'side': hp2obdata['side']}
            with open(self.sim_data['hp2']['recons']['json_path'], 'r') as f:
                hmplv2 = json.load(f)
            self.data['hmplv2'] = {'success': True, 'metadata': hmplv2}
            stitch = cv2.imread(f'{self.sim_data['hp2']['regs']['json_path'][:-4]}png')
            self.data['pelvis'] = {'success': True, 'stitch': stitch}
            vp1 = cv2.imread(f'{self.sim_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot1.png')
            self.viewpairs[1] = vp1
        if stage >= 5 and stage != 7:
            cupapimage = cv2.imread(self.sim_data['cup']['ap']['image_path'])
            with open(self.sim_data['cup']['ap']['json_path'], 'r') as f:
                cupapdata = json.load(f)
            self.data['cup-ap'] = {'image': cupapimage, 'framedata': cupapdata, 'success': True, 'side': cupapdata['side']}
            cupobimage = cv2.imread(self.sim_data['cup']['ob']['image_path'])
            with open(self.sim_data['cup']['ob']['json_path'], 'r') as f:
                cupobdata = json.load(f)
            self.data['cup-ob'] = {'image': cupobimage, 'framedata': cupobdata, 'success': True, 'side': cupobdata['side']}
            with open(self.sim_data['cup']['recons']['json_path'], 'r') as f:
                acecup = json.load(f)
            self.data['acecup'] = {'success': True, 'metadata': acecup}
            stitch = cv2.imread(f'{self.sim_data['cup']['regs']['json_path'][:-4]}png')
            with open(self.sim_data['cup']['regs']['json_path'], 'r') as f:
                cupdata = json.load(f)
            self.data['regcup'] = {'success': True, 'stitch': stitch, 'metadata': cupdata}
            vp2 = cv2.imread(f'{self.sim_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot2.png')
            self.viewpairs[2] = vp2
        if stage == 8:
            triapimage = cv2.imread(self.sim_data['tri']['ap']['image_path'])
            with open(self.sim_data['tri']['ap']['json_path'], 'r') as f:
                triapdata = json.load(f)
            self.data['tri-ap'] = {'image': triapimage, 'framedata': triapdata, 'success': True, 'side': triapdata['side']}
            triobimage = cv2.imread(self.sim_data['tri']['ob']['image_path'])
            with open(self.sim_data['tri']['ob']['json_path'], 'r') as f:
                triobdata = json.load(f)
            self.data['tri-ob'] = {'image': triobimage, 'framedata': triobdata, 'success': True, 'side': triobdata['side']}
            with open(self.sim_data['tri']['recons']['json_path'], 'r') as f:
                acetri = json.load(f)
            self.data['acecup'] = {'success': True, 'metadata': acetri}
            stitch = cv2.imread(f'{self.sim_data['tri']['regs']['json_path'][:-4]}png')
            with open(self.sim_data['tri']['regs']['json_path'], 'r') as f:
                tridata = json.load(f)
            self.data['regtri'] = {'success': True, 'stitch': stitch, 'metadata': tridata}
            vp3 = cv2.imread(f'{self.sim_data['hp1']['ap']['image_path'][:7]}/viewpairs/screenshot2.png')
            self.viewpairs[3] = vp3


    def getfrmcase(self, c):
        match c:
            case 'hmplv1': return ['hp1-ap', 'hp1-ob']
            case 'hmplv2'| 'pelvis': return ['hp2-ap', 'hp2-ob']
            case 'acecup'| 'regcup': return ['cup-ap', 'cup-ob']
            case 'tothip'| 'regtri': return ['tri-ap', 'tri-ob']


    def stitch_sim(self,section):

        [frmstr1, frmstr2] = self.getfrmcase(section)
        frame1 = self.data[frmstr1]['image']
        frame2 = self.data[frmstr2]['image']
        """Stitch two frames together."""
        if frame1.shape[0] != frame2.shape[0]:
            max_height = max(frame1.shape[0], frame2.shape[0])
            frame1_resized = cv2.resize(frame1, (int(frame1.shape[1] * max_height / frame1.shape[0]), max_height))
            frame2_resized = cv2.resize(frame2, (int(frame2.shape[1] * max_height / frame2.shape[0]), max_height))
        else:
            frame1_resized, frame2_resized = frame1, frame2
        # Simulate processing with progress updates
        k=0
        for i in range(1000):
            for j in range(3000):
                with self._lock:
                    self.progress = (k + 1) /30000
                    k+=1
        # Stitch the images
        result = np.hstack((frame1_resized, frame2_resized))
        return result

    def stitch_act(self,section):
        # return image array
        pass

    def stitch(self, section):
        if self.on_simulation:
            result = self.stitch_sim(section)
        else:
            result = self.stitch_act(section)
        return result

    def settest(self, testdata):
        self.sim_data = testdata

    def analyzeframe_sim(self, section, image, tilt_angle=None, rotation_angle=None):
        section_type = section[-2:]  # ap, ob
        test_entry = self.sim_data.get(section[:-3]).get(section_type)
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

        metadata['processed_frame'] = image
        metadata['imuangles'] = [tilt_angle, rotation_angle]

        self.calib['distortion'].update({(5, 20): {'data': {}}})
        self.calib['gantry'].update({(1.5, 0.2): {'data': {}}})
        framecalib = {}
        framecalib['distortion'] = self.calib['distortion']
        framecalib['gantry'] = self.calib['gantry']

        # simulate wait:
        #>> wait (self.sim_wait_values['frame_analysis'])?
        k = 0
        for i in range(1000):
            for j in range(3000):
                with self._lock:
                    self.progress = (k + 1) / 30000
                    k += 1


        if error_code is None:
            if not self.ai_mode:
                metadata['landmarks'] = None
                metadata['side'] = None
                metadata['analysis_success'] = None
            else: metadata['analysis_success'] = True
        else:
            metadata['analysis_success'] = False
            metadata['landmarks'] = None
            metadata['side'] = None
        metadata['analysis_error_code'] = error_code

        return metadata, framecalib


    def analyzeframe_act(self, section, frame, tilt_angle=None, rotation_angle=None):
        # actual frame analysis
        return (None, None)

    def analyzeframe(self, section, frame, tilt_angle=None, rotation_angle=None):
        if self.on_simulation:
            framedata, framecalib = self.analyzeframe_sim(section, frame, tilt_angle, rotation_angle)
        else:
            framedata, framecalib = self.analyzeframe_act(section, frame, tilt_angle, rotation_angle)

        analysis_parameters = {
            'extract_distortion': self.extract_distortion,
            'correct_distortion': self.correct_distortion,
            'extract_glyph': self.extract_glyph,
            'extract_tracking': self.extract_tracking,
            'extract_camcalib': self.extract_camcalib,
            'ai_mode': self.ai_mode
        }

        return framedata, analysis_parameters, framecalib



    def reconstruct_sim(self, section):
        curap = self.getfrmcase(section)[0]
        test_entry = self.sim_data.get(curap[:-3]).get('recons')
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

        if error_code is None:
            metadata['analysis_success'] = True
        else:
            metadata['analysis_success'] = False
            metadata['recondata'] = None
        metadata['analysis_error_code'] = error_code

        return metadata

    def reconstruct(self, section):
        # self.is_processing = True
        if self.on_simulation:
            recon_result = self.reconstruct_sim(section)
        else:
            recon_result = self.reconstruct_act(section)

        return recon_result



    def reg_sim(self, section):
        curap = self.getfrmcase(section)[0]
        test_entry = self.sim_data.get(curap[:-3]).get('regs')
        if test_entry and test_entry.get('json_path'):
            try:
                error_code = test_entry['errors']
                print(f"Simulating error {error_code} for {section}")
                with open(test_entry['json_path'], 'r') as f:
                    metadata = json.load(f)
                print(f"Using test data for {section}: {test_entry['file_name']}")
            except Exception as e:
                print(f"Error loading test JSON: {e}")
        else: metadata = None

        if error_code is None:
            metadata['analysis_success'] = True
            res = self.stitch(section)
            metadata['stitched_image'] = res
        else:
            metadata['analysis_success'] = False
            metadata['stitched_image'] = None
            metadata['regresult'] = None
            metadata['measurements'] = None
        metadata['analysis_error_code'] = error_code

        return metadata


    def reg(self, section):
        if self.on_simulation:
            reg_result = self.reg_sim(section)

        else:
            reg_result = self.reg_act(section)

        return reg_result

    def update(self, analysis_type, data):
        section = data['section']
        if analysis_type == 'frame':
            section_type = section[-2:]  # ap, ob
            # reset the 'ob' view if 'ap' image is repeated:
            if section_type == 'ap':
                tmp = section[:-2] + 'ob'
                self.data[tmp] = {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None}
                self.data[tmp]['side'] = self.data[section]['side']

            self.data[section]['image'] = data['processed_frame']
            self.data[section]['framedata'] = data
            self.data[section]['success'] = data['analysis_success']
            self.data[section]['side'] = data['side']
            self.data[section]['error_code'] = data['analysis_error_code']

        if analysis_type == 'recon':
            if section == 'hmplv1':
                self.data['hp2-ap']['side'] = 'l' if self.data['hp1-ap']['side'] == 'r' else 'r'
                self.data['hp2-ob']['side'] = self.data['hp2-ap']['side']
            if section == 'acecup':
                self.data['tri-ap']['side'] = self.data['cup-ap']['side']
                self.data['tri-ob']['side'] = self.data['tri-ap']['side']
            self.data[section]['success'] = data['analysis_success']
            self.data[section]['metadata'] = data['recondata']
            self.data[section]['error_code'] = data['analysis_error_code']

        if analysis_type == 'reg':
            self.data[section]['metadata'] = data['regresult']
            self.data[section]['success'] = data['analysis_success']
            self.data[section]['error_code'] = data['analysis_error_code']
            self.data[section]['stitch'] = data['stitched_image']


    def exec(self, scn, frame=None, tilt_angle=None, rotation_angle=None):
        print(scn)
        match scn:
            case 'frm:hp1-ap:bgn' | 'frm:hp1-ob:bgn' | 'frm:hp2-ap:bgn' | 'frm:hp2-ob:bgn' | 'frm:cup-ap:bgn' | 'frm:cup-ob:bgn' | 'frm:tri-ap:bgn' | 'frm:tri-ob:bgn':   
                try:

                    framedata, analysis_parameters, framecalib = self.analyzeframe(scn[4:-4], frame, tilt_angle, rotation_angle)
                    
                    # Prepare data for different components

                    data_for_model = framedata
                    data_for_calib = framecalib
                    data_for_exam = {
                        'framedata': framedata, 
                        'analysis_parameters': analysis_parameters, 
                        'framecalib': framecalib
                    }

                    return "frame", data_for_model, data_for_exam
                
                except Exception as error:
                    return "exception", {'type':'frame', 'success': False, 'error': str(error)}, None, None


            case 'rcn:hmplv1:bgn' | 'rcn:hmplv2:bgn' | 'rcn:acecup:bgn' | 'rcn:tothip:bgn':
                try:
                    recon_result= self.reconstruct(scn[4:-4])

                    #return dataforsave, dataforvm, processed_frame
                    data_for_model = recon_result
                    data_for_calib = None
                    data_for_exam = recon_result
                    
                    return 'recon', data_for_model, data_for_exam
                
                except Exception as error:
                    return 'exception', {'type': 'recon', 'success': False, 'error': str(error)}, None, None

            
            case 'reg:pelvis:bgn' | 'reg:regcup:bgn' | 'reg:regtri:bgn':
                try:
                    reg_result = self.reg(scn[4:-4])
                    
                    #return dataforsave, dataforvm, processed_frame
                    data_for_model = reg_result
                    data_for_calib = None
                    data_for_exam = reg_result

                    return 'reg', data_for_model, data_for_exam

                except Exception as error:
                    return 'exception', {'type': 'reg', 'success': False, 'error': str(error)}, None, None


            case _:
                return None, None, None

    # return the corresponding rcn (reconstruction) scenario for a given frame str: 'hp1', 'hp2', 'cup', or 'tri':
    def __get_frm_strs__(self, frm_scn):
        stgstr = frm_scn[4:7]
        frm = Frm()


        match stgstr:
            case 'hp1':
                frm.rcn = 'hmplv1'
            case 'hp2':
                frm.rcn = 'hmplv2'
            case 'cup':
                frm.rcn = 'acecup'
            case 'tri':
                frm.rcn = 'tothip'

        frm.ap = stgstr + '-ap'
        frm.ob = stgstr + '-ob'
        if stgstr == 'cup':
            frm.next_ap = 'tri-ap'
            frm.next_ob = 'tri-ob'
        if stgstr == 'tri':
            frm.prev_ap = 'cup-ap'
            frm.prev_ob = 'cup-ob'
        return frm


    def __get_rcn_strs__(self, rcn_scn):
        rcnstr = rcn_scn[4:10]
        rcn = Rcn()
        rcn.rcn = rcnstr

        match rcnstr:
            case 'hmplv1':
                stgstr = 'hp1'
            case 'hmplv2':
                stgstr= 'hp2'
                rcn.reg = 'pelvis'
            case 'acecup':
                stgstr= 'cup'
                rcn.reg = 'regcup'
            case 'tothip':
                stgstr = 'tri'
                rcn.reg = 'regtri'
        rcn.ap = stgstr + '-ap'
        rcn.ob = stgstr + '-ob'
        return rcn

    def __get_reg_strs__(self, reg_scn):
        regstr = reg_scn[4:10]
        reg = Reg()
        reg.reg = regstr

        match regstr:
            case 'pelvis':
                stgstr = 'hp2'
                stgstr2 = 'cup'
                reg.rcn = 'hmplv2'
            case 'regcup':
                stgstr= 'cup'
                stgstr2 = 'tri'
                reg.rcn = 'acecup'
            case 'regtri':
                stgstr= 'tri'
                stgstr2 = 'tri'
                reg.rcn = 'tothip'
        reg.ap = stgstr + '-ap'
        reg.ob = stgstr + '-ob'
        reg.next_ap = stgstr2 + '-ap'
        reg.next_ob = stgstr2 + '-ob'
        return reg

    def copy_stage_data(self, source_stage, target_stage):

        source_ap = (source_stage + '-ap')
        source_ob = (source_stage + '-ob')
        target_ap = (target_stage + '-ap')
        target_ob = (target_stage + '-ob')

        self.data[target_ap] = {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None}
        self.data[target_ob] = {'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None}
        self.data[target_ap]['image'] = self.data[source_ap]['image']
        self.data[target_ob]['image'] = self.data[source_ob]['image']
        return

    def set_success_to_none(self, stage):
        self.data[stage]['success'] = None


    def __eval_frm_scn__(self, scn, active_side, frame_not_none, uistates):
        frm = self.__get_frm_strs__(scn)
        action = None
        if frame_not_none: print(2,scn,frm.ob,frm.next_ap,uistates)
        if uistates is not None:
            match (uistates):
                case 'prev':
                    #self.__copy_stage_data__('prev')  # check logic!
                    action = ('copy_stage_data', 'tri', 'cup')
                    scn = ('frm:' + 'cup-ap' + ':end')
                case 'next':
                    if frm.rcn == 'acecup':
                        action = ('copy_stage_data', 'cup', 'tri')
                        scn = ('frm:' + frm.next_ap + ':end')
                case 'landmarks':
                    if self.data[frm.ap]['framedata']['landmarks'] and self.data[frm.ob]['framedata']['landmarks']:
                        scn = ('rcn:' + frm.rcn + ':bgn')
            uistates = None
        else:
            if self.data[frm.ap]['success'] and self.data[frm.ob]['success']:
                scn = ('rcn:' + frm.rcn + ':bgn')
            else:
                if frame_not_none:
                    if active_side == 'ap':
                        scn = ('frm:' + frm.ap + ':bgn')
                    if active_side == 'ob':
                        scn = ('frm:' + frm.ob + ':bgn')
        return uistates, scn, action

    def __eval_rcn_scn__(self, scn, active_side, frame_not_none, uistates):
        rcn = self.__get_rcn_strs__(scn)
        action = None
        
        if self.data[rcn.rcn]['success']:
            
            #exceptional scenario for hmplv1 only:
            if rcn.rcn == 'hmplv1':
                if uistates == 'next':
                    if frame_not_none:
                        uistates = None
                        if active_side == 'ap' or active_side =='ob':
                            scn = ('frm:hp2-' + active_side + ':bgn')
                            return uistates, scn, action
            else:
                scn = ('reg:' + rcn.reg + ':bgn')
                return uistates, scn, action
            

        if uistates == 'landmarks':
            uistates = None
            scn = ('rcn:' + rcn.rcn + ':bgn')
        else:
            # user does nothing/ editing
            # they can retake
            if frame_not_none:
                if active_side == 'ap':
                    #self.__set_success_to_none__(rcn.ap)
                    action = ('set_success_to_none', rcn.ap)
                    scn = ('frm:' + rcn.ap + ':bgn')
                if active_side == 'ob':
                    #self.__set_success_to_none__(rcn.ob)
                    action = ('set_success_to_none', rcn.ob)
                    scn = ('frm:' + rcn.ob + ':bgn')

        return uistates, scn, action


    def __eval_reg_scn__(self, scn, active_side, frame_not_none, uistates):
        reg = self.__get_reg_strs__(scn)
        action = None

        # exception if pelvis registration fails:
        if not self.data[reg.reg]['success']:
            if uistates == 'restart':
                if frame_not_none:
                    uistates = None
                    if active_side == 'ap':
                        scn = 'frm:hp1-ap:bgn'
                    if active_side == 'ob':
                        scn = 'frm:hp1-ob:bgn'
                    return uistates, scn, action

        # additional provisions for pelvis and cup registration (next & skip options)

        if self.data[reg.reg]['success']:
            if (reg.reg == 'regcup'):
                #self.__set_imu_setcupreg__()
                action =('set_imu_setcupreg')

        if uistates == 'next':
            if frame_not_none:
                if active_side == 'ap':
                    scn = ('frm:' + reg.next_ap + ':bgn')
                if active_side == 'ob':
                    scn = ('frm:' + reg.next_ob + ':bgn')
                uistates = None
                return uistates, scn, action

        if uistates == 'skip':
            if frame_not_none:
                if active_side == 'ap':
                    scn = 'frm:tri-ap:bgn'
                if active_side == 'ob':
                    scn = 'frm:tri-ob:bgn'
                uistates = None
                return uistates, scn, action

        # common for all 3 registration types:
        if uistates == 'landmarks':
            uistates = None
            scn = ('rcn:' + reg.rcn + ':bgn')
        else:
            # user does nothing/ editing
            # they can retake
            if frame_not_none:
                if active_side == 'ap':
                    #self.__set_success_to_none__(reg.ap)
                    action = ('set_success_to_none', reg.ap)
                    scn = ('frm:' + reg.ap + ':bgn')
                if active_side == 'ob':
                    #self.__set_success_to_none__(reg.ob)
                    action = ('set_success_to_none', reg.ob)
                    scn = ('frm:' + reg.ob + ':bgn')
        return uistates, scn, action


    def eval_modelscnario(self, frame, scn, active_side, uistates):
        frame_not_none = frame is not None
        if(frame_not_none):print(3,scn,uistates)
        action = None
        match scn:
            case 'init':
                if frame is not None:
                    if active_side == 'ap':
                        scn = 'frm:hp1-ap:bgn'
                    if active_side == 'ob':
                        scn = 'frm:hp1-ob:bgn'
                else: scn = 'init'

            case 'frm:hp1-ap:end' | 'frm:hp1-ob:end' | 'frm:hp2-ap:end' | 'frm:hp2-ob:end' | 'frm:cup-ap:end' | 'frm:cup-ob:end' | 'frm:tri-ap:end' | 'frm:tri-ob:end':
                uistates, scn, action = self.__eval_frm_scn__(scn, active_side, frame_not_none, uistates)

            case 'rcn:hmplv1:end' | 'rcn:hmplv2:end' | 'rcn:acecup:end' | 'rcn:tothip:end':
                uistates, scn, action = self.__eval_rcn_scn__(scn, active_side, frame_not_none, uistates)

            case 'reg:pelvis:end' | 'reg:regcup:end' | 'reg:regtri:end':
                uistates, scn, action = self.__eval_reg_scn__(scn, active_side, frame_not_none, uistates)

        return scn, uistates, action

    def get_model_states(self):
        return {'progress': self.progress}

    # controller
    #>> keep active_side as a controller parameter
    #>> make viewmodel.states['active_side'] update based on controller.active_side in the controller.update_vm_states?

    