import cv2
import numpy as np
import time
import threading
import json
import datetime
import copy
from calibrate import Calibrate
from hip_ml_models.hip_models import HipModels, HipModelConfig
import confirmap_dataclasses.frame_data as dataclass
import confirmap_dataclasses.bmodel_data as bmodel
import confirmap_dataclasses as cdc
from frame_process.frame_processor import frame_processor
import pose as pose

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
    def __init__(self, ai_mode = True, on_simulation = False, config = None, carm = None, bugs = None, logger = None):

        self.carm = carm
        self.calib_lookup = {}

        self.config = config

        pose.config.config.update_from_dict(config.get('reconreg_config'))

        self.shot_count = 0
        self.bm_count = 0 

        self.ai_mode = ai_mode
        self.on_simulation = on_simulation

        self.progress = 0

        self.viewpairs = [None]*4

        self.data = None
        self._resetdata()
        self.sim_data = None
        self.patient_data = None
        self.angles = None
        self.bugs = bugs
        self.logger = logger

        self.default_templates = []
        self.default_tables = []

        self._lock = threading.Lock()
        self._stitch_thread = None
        # wait in seconds: use this values for waiting in seconds during analysis
        self._sim_wait_values ={
            'frame_analysis': 2,
            'recon': 2,
            'reg': 2
        }

        self.calibrate = Calibrate()
        self.cnn = self.load_cnn() #self.cnn = CNN()
  
        self.fp = frame_processor(cdc.HardwareClass(**carm), config)

    def _resetdata(self):
        self.viewpairs = [None]*4
        self.data = {
            'frame':{
                'hp1-ap': dataclass.FrameData(),
                'hp1-ob': dataclass.FrameData(),
                'hp2-ap': dataclass.FrameData(),
                'hp2-ob': dataclass.FrameData(),
                'cup-ap': dataclass.FrameData(),
                'cup-ob': dataclass.FrameData(),
                'tri-ap': dataclass.FrameData(),
                'tri-ob': dataclass.FrameData(),
            },
            'latest_state':{
                'hp1-ap': {'success': None, 'error_code': None},
                'hp1-ob': {'success': None, 'error_code': None},
                'hmplv1': {'success': None, 'error_code': None},

                'hp2-ap': {'success': None, 'error_code': None},
                'hp2-ob': {'success': None, 'error_code': None},
                'hmplv2': {'success': None, 'error_code': None},
                'pelvis': {'success': None, 'error_code': None},

                'cup-ap': {'success': None, 'error_code': None},
                'cup-ob': {'success': None, 'error_code': None},
                'acecup': {'success': None, 'error_code': None},
                'regcup': {'success': None, 'error_code': None},

                'tri-ap': {'success': None, 'error_code': None},
                'tri-ob': {'success': None, 'error_code': None},
                'tothip': {'success': None, 'error_code': None},
                'regtri': {'success': None, 'error_code': None},
            },
            'bmodel': bmodel.BModelData(),
            'report': {},
            'exp_side':{
                'hp2-ap': None,
                'hp2-ob': None,
                'tri-ap': None,
                'tri-ob': None}
        }


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

    def load_cnn(self):
        p = self.config.get('frame_prediction_config')
        cfg = HipModelConfig('./config/models', 
                         later_cls_name = p["classifier_model_path"], 
                         ref_lm_name = p["ref_annotator_model_path"], 
                         ref_seg_name = p["ref_segmentor_model_path"], 
                         cup_lm_name = p["cup_annotator_model_path"],
                         cup_seg_name = p["cup_segmentor_model_path"],
                         trial_lm_name = p["trl_annotator_model_path"],
                         trial_seg_name = p["trl_segmentor_model_path"],
                         phase="all")
        return HipModels(config = cfg)

    def pre_process(self, obj):
        #self.calib['distortion'].update({(5, 20): {'data': {}}})
        #self.calib['gantry'].update({(1.5, 0.2): {'data': {}}})
        '''framecalib = {}
        framecalib['distortion'] = self.calib['distortion']
        framecalib['gantry'] = self.calib['gantry']
        return framecalib, frame, None'''

        framecalib = dataclass.CalibrationData(datasource="FrameGrabber", version="v1")
        framecalib.camera = dataclass.CameraData(
            intrinsic_matrix=[
      [
        2624.671875,
        0.0,
        985.7281494140625
      ],
      [
        0.0,
        2624.671875,
        985.3087768554688
      ],
      [
        0.0,
        0.0,
        1.0
      ]
    ],
            extrinsic_matrix=[
      [
        0.028930891305208206,
        -0.9657391905784607,
        -0.25789690017700195,
        91.86577606201172
      ],
      [
        0.9937665462493896,
        -3.84761077165674e-11,
        0.11148080229759216,
        -32.285743713378906
      ],
      [
        -0.10766137391328812,
        -0.25951457023620605,
        0.9597193002700806,
        513.8992919921875
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ]
    ],
            sensor_width=2000,
            sensor_height=2000,
            pixel_size=0.30479999999999996,
            source_to_detector_distance=800,
            source_in_world=[
      84.75384521484375,
      222.08273315429688,
      -465.9079284667969
    ],
            piercing_point=[
      -4.350065000668597,
      -4.477878509684685
    ],
            corners=[
      [
        150.2415313720703,
        157.44869995117188,
        357.5380859375
      ],
      [
        159.05966186523438,
        -136.9086151123047,
        278.93109130859375
      ],
      [
        -143.8404083251953,
        -136.9086151123047,
        244.95175170898438
      ],
      [
        -152.65853881835938,
        157.44869995117188,
        323.5587158203125
      ]
    ],
        )

        #crop_obj = self.fp.analyze(obj)

        return framecalib, obj.image


    
    def process(self, obj):
        t0 = time.perf_counter()
        ann = self.cnn.predict(frame = obj)
        dt = time.perf_counter() - t0
        print("----------------------------",dt)
        return ann



    def analyzeframe_sim(self, section, frame, tilt_angle=None, rotation_angle=None, act_tilt=None, act_rot=None):
        obj = dataclass.FrameData()
        obj.meta.index = self.shot_count
        self.shot_count += 1
        obj.meta.op_stage = section
        obj.meta.carm_view = section[-2:]
        obj.raw_image = frame
        obj.image = frame
        #obj.raw_image = self.fp.create_raw_image(obj)
        obj.meta.carm_angles = [tilt_angle, rotation_angle]
        obj.meta.carm_angles_actual = [act_tilt, act_rot]

        obj.meta.frame_cropping_config = self.carm.get('frame_cropping_config')
        #self.config.get('frame_analysis_config').ai_mode = self.ai_mode
        obj.meta.frame_analysis_config = self.config.get('frame_analysis_config')
    

        framecalib, crop_image = self.pre_process(obj)

        if act_tilt and act_rot:
            k = f'T{act_tilt}_R{act_rot}'
            if obj.calibration is None:
                obj.calibration = self.calib_lookup[k]
            else:
                self.calib_lookup.update({k: obj.calibration})

        obj.image = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
        error_code = framecalib.error_code
        obj.calibration = framecalib
        if error_code is not None:
            return obj
        if not self.ai_mode:
            return obj
        
        anno = self.process(obj)

        if 'hp2' in section or 'tri' in section:
            if anno.side != None and self.data['exp_side'][section] != anno.side:
                anno.success = False
                anno.error_code = '115'
                anno.landmarks = {}
            anno.side = self.data['exp_side'][section]

        if 'ob' in section:
            apsec = section[:-2] + 'ap'
            if (anno.side == 'left' and self.data['frame'][apsec].meta.side == 'right') or (anno.side == 'right' and self.data['frame'][apsec].meta.side == 'left'):
                anno.success = False
                anno.error_code = '115'
                anno.landmarks = {}
        
        
        num = 2 if 'cup' in section else 4 if 'tri' in section else 0
        ui_objects = self.update_ui_objects(anno.landmarks, self.default_templates[num])

        obj.annotations['default'] = anno

        obj.ui_objects = ui_objects
        obj.meta.side = anno.side

        return obj


    def analyzeframe_act(self, section, frame, tilt_angle=None, rotation_angle=None, act_tilt=None, act_rot=None):
        # actual frame analysis
        
        framecalib, image, error_code = self.calibrate.pre_process(section, frame, tilt_angle=None, rotation_angle=None, act_tilt=None, act_rot=None)
        if error_code is not None:
            return {}
        if not self.ai_mode:
            return {}
        
        metadata = self.cnn.process(section, image)

        
        num = 2 if 'cup' in section else 4 if 'tri' in section else 0
        metadata['ui_objects'] = self.update_ui_objects(metadata['landmarks'], self.default_templates[num])

        return metadata, framecalib


    def analyzeframe(self, section, frame, tilt_angle=None, rotation_angle=None, act_tilt=None, act_rot=None):
        if self.on_simulation:
            tmp_obj = self.analyzeframe_sim(section, frame, tilt_angle, rotation_angle, act_tilt, act_rot)
        else:
            tmp_obj = self.analyzeframe_sim(section, frame, tilt_angle, rotation_angle, act_tilt, act_rot)

        return tmp_obj



    def reconstruct_sim(self, section):
        '''
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
            metadata['shot_1'] = self.data[curap]['framedata']
            curob = curap[:-3] + '-ob'
            metadata['shot_2'] = self.data[curob]['framedata']
        else:
            metadata['analysis_success'] = False
            metadata['recondata'] = None
        metadata['analysis_error_code'] = error_code
        k = 0
        for i in range(10000):p
            for j in range(1000):
                with self._lock:
                    self.progress = (k + 1) / 100000
                    k += 1

        return metadata
        '''
        shot_1, shot_2 = 'hp1-ap', 'hp1-ob'
        if section == 'hmplv2': shot_1, shot_2 = 'hp2-ap', 'hp2-ob'
        if section == 'acecup': shot_1, shot_2 = 'cup-ap', 'cup-ob'
        if section == 'tothip': shot_1, shot_2 = 'tri-ap', 'tri-ob'
        res = pose.analyze(section, bmodel=self.data['bmodel'], frame_ap=self.data['frame'][shot_1], frame_ob=self.data['frame'][shot_2])

        res.metadata.index = self.bm_count
        res.metadata.last_op = section
        res.metadata.last_op_data = {'ap': self.data['frame'][shot_1].meta.index, 'ob': self.data['frame'][shot_2].meta.index}
        self.bm_count += 1

        return res
    

    def reconstruct(self, section):
        # self.is_processing = True
        if self.on_simulation:
            recon_result = self.reconstruct_sim(section)
        else:
            recon_result = self.reconstruct_act(section)

        return recon_result


    def reg_sim(self, section):
        '''
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
        '''

        res = pose.analyze(section, bmodel=self.data['bmodel'], patient={})
        mea = None if section == 'pelvis' else {
        "Inclination" : "41",
        "Anteversion" : "31"
    } if 'cup' in section else {
        "LLD" : "3mm",
        "Offset" : "5mm"
    }#measure()
        
        res.metadata.last_op = section
        res.metadata.last_op_data = {'recon': self.data['bmodel'].metadata.index}
        res.metadata.index = self.bm_count
        self.bm_count += 1
        return res, mea


    def reg(self, section):
        if self.on_simulation:
            reg_result = self.reg_sim(section)

        else:
            reg_result = self.reg_act(section)

        return reg_result

    def update_ui_objects(self, LandmarksData, tp, red = False, use_table = None):
        print(11,LandmarksData)
        if not LandmarksData: return {}
        tb = {}
        if use_table: tb = use_table
        else:
            for g, LandmarkGroup in LandmarksData.items():
                for l, LandmarkData in LandmarkGroup.items():
                    tb[LandmarkData.label] = LandmarkData.coords
        print(tb)
        
        temp = copy.deepcopy(tp)
        rt = {}
        for g in temp:
            rt[g] = []
            handle = None

            for s in temp[g]:
                if s['type'] == 'handle':
                    handle = [400, 400]
                elif s['type'] == 'line':
                    if red: s['template'] = 1
                    s['type'] = 'lines'
                    s['points'] = tb[s['id']]
                    rt[g].append(s)
                else:
                    for i in range(len(s['keys'])):
                        if red: s['template'] = 1
                        k = f'_{s['keys'][i]}'
                        if k not in tb: 
                            continue
                        s['points'].append(tb[k][0])
                        s['type'] = 'lines' if 'point' in s['type'] else s['type']
                        
                    rt[g].append(s)

            rt[g][0]['handle'] = handle

        return rt

    def uidict_to_landmark(self, uidict, landmark):
        if not landmark:
            newdict = {}
            for g in uidict:
                gdict = {}
                for p in uidict[g]:
                    gdict[p['id']] = dataclass.Landmark2dData(
                        label=p['id'],
                        type="point",
                        coords=p['points'],
                        confidence=[1],
                        visible=True,
                    )
                print(p['points'])
                gdict["Head Center"] = dataclass.Landmark2dData(
                    label="Head Center",
                    type="point",
                    coords=p['points'],
                    confidence=[1],
                    visible=True,
                )
                gdict["Lesser Trochanter"] = dataclass.Landmark2dData(
                    label="Lesser Trochanter",
                    type="point",
                    coords=p['points'],
                    confidence=[1],
                    visible=True,
                )
                gdict["Proximal Shaft"] = dataclass.Landmark2dData(
                    label="proximal shaft",
                    type="point",
                    coords=[
              [
                645.0086059570312,
                836.7146606445312
              ],
              [
                613.4690551757812,
                1039.071533203125
              ]
            ],
                    confidence=[1],
                    visible=True,
                )
                gdict["Neck Shaft"] = dataclass.Landmark2dData(
                    label="neck shaft",
                    type="point",
                    coords=[
              [
                523.4983520507812,
                527.8784790039062
              ],
              [
                645.8402709960938,
                692.1206665039062
              ]
            ],
                    confidence=[1],
                    visible=True,
                )
                if g == 'pelvis':
                    newdict['hpelv'] = gdict
                else: newdict[g] = gdict
                newdict['cup'] = gdict
            return newdict
        
        for g in uidict:
            for p in uidict[g]:
                if p['keys'][0] in landmark[f'{g}_1']:
                    landmark[f'{g}_1'][p['keys'][0]].coords = p['points']
                elif p['id'] in landmark[f'{g}_1']:
                    landmark[f'{g}_1'][p['id']].coords = p['points']

        return landmark
        


    def update(self, analysis_type, data, section):
        try:

            if analysis_type == 'frame':

                section_type = section[-2:]  # ap, ob
                # reset the 'ob' view if 'ap' image is repeated:
                if section_type == 'ap':
                    tmp = section[:-2] + 'ob'
                    self.data['latest_state'][tmp] = {'success': None, 'error_code': None}
                
                self.data['frame'][section] = data

                self.data['latest_state'][section]['error_code'] = data.annotations['default'].error_code
                self.data['latest_state'][section]['success'] = data.annotations['default'].success
                

            if analysis_type == 'recon':
                
                
                self.data['latest_state'][section]['success'] = data.state['success']
                self.data['latest_state'][section]['error_code'] = data.state['error_code']
                if data.state['success']:
                    self.data['bmodel'] = data
                    shot_1, shot_2 = 'hp1-ap', 'hp1-ob'
                    if section == 'hmplv2': shot_1, shot_2 = 'hp2-ap', 'hp2-ob'
                    if section == 'acecup': shot_1, shot_2 = 'cup-ap', 'cup-ob'
                    if section == 'tothip': shot_1, shot_2 = 'tri-ap', 'tri-ob'

                    self.angles = [self.data['frame'][shot_1].meta.carm_angles[0], self.data['frame'][shot_1].meta.carm_angles[1], self.data['frame'][shot_2].meta.carm_angles[1]]

                    if section == 'hmplv1':
                        self.data['exp_side']['hp2-ap'] = 'left' if self.data['frame']['hp1-ap'].meta.side == 'right' else 'right'
                        self.data['exp_side']['hp2-ob'] = self.data['exp_side']['hp2-ap']
                    if section == 'acecup':
                        self.data['exp_side']['tri-ap'] = 'left' if self.data['frame']['cup-ap'].meta.side == 'right' else 'right'
                        self.data['exp_side']['tri-ob'] = self.data['exp_side']['tri-ap']

            if analysis_type == 'reg':
                #self.data[section]['metadata'] = data['regresult']
                self.data['latest_state'][section]['success'] = data.state['success']
                self.data['latest_state'][section]['error_code'] = data.state['error_code']
                if data.state['success']:
                    self.data['bmodel'] = data
                #self.data[section]['stitch'] = data['stitched_image']
        except Exception as e:
            self.bugs[0] = str(e)
            self.bugs.append(str(e))
            self.logger.error(f'Exception in {self.__class__.__name__}: {str(e)}')


    def exec(self, scn, frame=None, tilt_angle=None, rotation_angle=None, act_tilt=None, act_rot=None):
        match scn:
            case 'frm:hp1-ap:bgn' | 'frm:hp1-ob:bgn' | 'frm:hp2-ap:bgn' | 'frm:hp2-ob:bgn' | 'frm:cup-ap:bgn' | 'frm:cup-ob:bgn' | 'frm:tri-ap:bgn' | 'frm:tri-ob:bgn':   


                tmp_obj = self.analyzeframe(scn[4:-4], frame, tilt_angle, rotation_angle, act_tilt, act_rot)

                
                # Prepare data for different components

                data_for_model = tmp_obj
                data_for_vm = {
                    'processed_frame': tmp_obj.image,
                    'ui_objects': tmp_obj.ui_objects,
                    'analysis_error_code': tmp_obj.annotations['default'].error_code,
                    'side': tmp_obj.annotations['default'].side
                }
                data_for_exam = tmp_obj

                self.update("frame", data_for_model, scn[4:-4])

                return "frame", data_for_vm, data_for_exam
                



            case 'rcn:hmplv1:bgn' | 'rcn:hmplv2:bgn' | 'rcn:acecup:bgn' | 'rcn:tothip:bgn':
                
                recon_result= self.reconstruct(scn[4:-4])

                #return dataforsave, dataforvm, processed_frame
                data_for_model = recon_result
                data_for_vm = {'analysis_error_code': recon_result.state['error_code'][0] if len(recon_result.state['error_code']) > 0 else None}
                data_for_exam = recon_result

                self.update("recon", data_for_model, scn[4:-4])
                
                return 'recon', data_for_vm, data_for_exam
                
    
            
            case 'reg:pelvis:bgn' | 'reg:regcup:bgn' | 'reg:regtri:bgn':
                
                reg_result, mea = self.reg(scn[4:-4])
                
                #return dataforsave, dataforvm, processed_frame
                data_for_model = reg_result
                data_for_vm = {'measurements': mea,
                               'analysis_error_code': reg_result.state['error_code'][0] if len(reg_result.state['error_code']) > 0 else None}
                data_for_exam = reg_result

                self.update("reg", data_for_model, scn[4:-4])

                return 'reg', data_for_vm, data_for_exam



            case _:
                return None, None, None

    # return the corresponding rcn (reconstruction) scenario for a given frame str: 'hp1', 'hp2', 'cup', or 'tri':
    def __get_frm_strs__(self, frm_scn):
        stgstr = frm_scn[4:7]
        frm = Frm()


        match stgstr:
            case 'hp1':
                frm.rcn = 'hmplv1'
                stgstr2 = 'hp2'
            case 'hp2':
                frm.rcn = 'hmplv2'
                stgstr2 = 'cup'
            case 'cup':
                frm.rcn = 'acecup'
                stgstr2 = 'tri'
            case 'tri':
                stgstr2 = 'tri'
                frm.rcn = 'tothip'

        frm.ap = stgstr + '-ap'
        frm.ob = stgstr + '-ob'

        frm.next_ap = stgstr2 + '-ap'
        frm.next_ob = stgstr2 + '-ap'

        return frm


    def __get_rcn_strs__(self, rcn_scn):
        rcnstr = rcn_scn[4:10]
        rcn = Rcn()
        rcn.rcn = rcnstr

        match rcnstr:
            case 'hmplv1':
                stgstr = 'hp1'
                stgstr2 = 'hp2'
            case 'hmplv2':
                stgstr= 'hp2'
                stgstr2 = 'cup'
                rcn.reg = 'pelvis'
            case 'acecup':
                stgstr= 'cup'
                stgstr2 = 'tri'
                rcn.reg = 'regcup'
            case 'tothip':
                stgstr = 'tri'
                stgstr2 = 'tri'
                rcn.reg = 'regtri'
        rcn.ap = stgstr + '-ap'
        rcn.ob = stgstr + '-ob'
        rcn.next_ap = stgstr2 + '-ap'
        rcn.next_ob = stgstr2 + '-ap'
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
        try:

            source_ap = (source_stage + '-ap')
            source_ob = (source_stage + '-ob')
            target_ap = (target_stage + '-ap')
            target_ob = (target_stage + '-ob')

            self.data['frame'][target_ap] = dataclass.FrameData()#{'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None}
            self.data['frame'][target_ob] = dataclass.FrameData()#{'image': None, 'framedata': None, 'success': False, 'side': None, 'error_code': None}
            self.data['frame'][target_ap].image = self.data['frame'][source_ap].image
            self.data['frame'][target_ob].image = self.data['frame'][source_ob].image
            self.data['latest_state'][target_ap] = {'success': None, 'error_code': None}
            self.data['latest_state'][target_ob] = {'success': None, 'error_code': None}
            if self.data['latest_state']['regcup']['success']:
                self.data['frame'][target_ap].meta.side = self.data['frame'][source_ap].meta.side
                self.data['frame'][target_ob].meta.side = self.data['frame'][source_ob].meta.side
            
        except Exception as e:
            self.bugs[0] = str(e)
            self.bugs.append(str(e))
            self.logger.error(f'Exception in {self.__class__.__name__}: {str(e)}')

    def set_success_to_none(self, stage):
        self.data[stage]['success'] = None


    def __eval_frm_scn__(self, scn, active_side, frame_not_none, uistates):
        frm = self.__get_frm_strs__(scn)
        action = None

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
                case 'skip':
                    scn = ('frm:' + 'tri-ap' + ':end')
                case 'landmarks':
                    if self.data['latest_state'][frm.ap]['success'] and self.data['latest_state'][frm.ob]['success']:
                        scn = ('rcn:' + frm.rcn + ':bgn')
            uistates = None
        else:
            if self.data['latest_state'][frm.ap]['success'] and self.data['latest_state'][frm.ob]['success']:
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
        
        if self.data['latest_state'][rcn.rcn]['success']:
            
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
            
        if uistates == 'prev':
            action = ('copy_stage_data', 'tri', 'cup')
            scn = ('frm:' + 'cup-ap' + ':end')
            uistates = None
            return uistates, scn, action

        if uistates == 'next':
            if rcn.rcn == 'acecup':
                action = ('copy_stage_data', 'cup', 'tri')
            scn = ('frm:' + rcn.next_ap + ':end')

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

        if uistates == 'landmarks':
            uistates = None
            scn = ('rcn:' + rcn.rcn + ':bgn')
        else:
            # user does nothing/ editing
            # they can retake
            if frame_not_none:
                if active_side == 'ap':
                    #self.__set_success_to_none__(rcn.ap)
                    #action = ('set_success_to_none', rcn.ap)
                    scn = ('frm:' + rcn.ap + ':bgn')
                if active_side == 'ob':
                    #self.__set_success_to_none__(rcn.ob)
                    #action = ('set_success_to_none', rcn.ob)
                    scn = ('frm:' + rcn.ob + ':bgn')

        return uistates, scn, action


    def __eval_reg_scn__(self, scn, active_side, frame_not_none, uistates):
        reg = self.__get_reg_strs__(scn)
        action = None

        # exception if pelvis registration fails:
        if not self.data['latest_state'][reg.reg]['success']:
            if uistates == 'restart':
                if frame_not_none:
                    uistates = None
                    if active_side == 'ap':
                        scn = 'frm:hp1-ap:bgn'
                    if active_side == 'ob':
                        scn = 'frm:hp1-ob:bgn'
                    return uistates, scn, action

        # additional provisions for pelvis and cup registration (next & skip options)

        if self.data['latest_state'][reg.reg]['success']:
            if reg.reg == 'regcup' or reg.reg == "regtri":
                #self.__set_imu_setcupreg__()
                action =('set_imu_setcupreg', '')

        if uistates == 'prev':
            action = ('copy_stage_data', 'tri', 'cup')
            scn = ('frm:' + 'cup-ap' + ':end')
            uistates = None
            return uistates, scn, action
            
        if uistates == 'next':
            if reg.rcn == 'acecup':
                action = ('copy_stage_data', 'cup', 'tri')
            scn = ('frm:' + reg.next_ap + ':end')

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
                    #action = ('set_success_to_none', reg.ap)
                    scn = ('frm:' + reg.ap + ':bgn')
                if active_side == 'ob':
                    #self.__set_success_to_none__(reg.ob)
                    #action = ('set_success_to_none', reg.ob)
                    scn = ('frm:' + reg.ob + ':bgn')
        return uistates, scn, action


    def eval_modelscnario(self, frame, scn, active_side, uistates):
        try:
            frame_not_none = frame is not None
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
        except Exception as e:
            errname = 'eval_modelscnario: ' + str(e)
            if errname != self.bugs[-1]:
                self.bugs[0] = str(e)
                self.bugs.append(errname)
                self.logger.error(f'Exception in {self.__class__.__name__}: {errname}')
            return scn, None, None

    def get_model_states(self):
        return {'progress': self.progress}

 

        