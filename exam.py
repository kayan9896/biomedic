import cv2
import os
import json
import shutil

class Exam:
    def __init__(self, calib_folder, bugs = None, logger = None):
        self.mx = self.checkmax()
        self.exam_folder = f'exams/exam{self.mx}'
        self.shot_count = 0
        self.recon_count = 0
        self.reg_count = 0  
        self.carm = os.path.basename(calib_folder)
        self.copyfile(calib_folder)
        self.bugs = bugs
        self.logger = logger

    def checkmax(self):
        mx = 0
        os.makedirs(os.path.join('./','exams'), exist_ok=True)
        for folder in os.listdir('./exams'):
            mx = max(mx, int(folder[4 :]) + 1)
        return mx

    def copyfile(self, calib_folder):
        shutil.copytree(calib_folder,os.path.join(self.exam_folder, self.carm))

    def save_json(self, data, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    def get_formatted_filename(self, prefix, data_type, count):
        """Generate filename with format: [Prefix]-[Count]-[Type].extension"""
        count_str = f'{count:03d}'  # Format as 3-digit string with leading zeros
        return f"{prefix}-{count_str}-{data_type}"

    #self.exam.save(analysis_type, data_for_exam, frame)
    def save(self, analysis_type, data_for_exam, rawframe=None):

        try:
            if analysis_type == 'frame':

                framedata = data_for_exam['framedata']
                analysis_parameters = data_for_exam['analysis_parameters']
                framecalib = data_for_exam['framecalib']
                data_type = framedata.get('section', 'unknown')  # Get type or default to 'unknown'

                # Save raw frame with 'W' prefix
                if rawframe is not None:
                    raw_filename = self.get_formatted_filename('W', data_type, self.shot_count) + '.png'
                    raw_path = os.path.join(self.exam_folder, 'shots/rawframes', raw_filename)
                    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
                    cv2.imwrite(raw_path, rawframe)

                # Save shot with 'S' prefix
                if framedata['processed_frame'] is not None:
                    shot_filename = self.get_formatted_filename('S', data_type, self.shot_count) + '.png'
                    shot_path = os.path.join(self.exam_folder, 'shots', shot_filename)
                    os.makedirs(os.path.dirname(shot_path), exist_ok=True)
                    cv2.imwrite(shot_path, framedata['processed_frame'])

                if 'distortion' in framecalib:
                    for k, v in framecalib['distortion'].items():
                        t, r = int(k[0] * 10), int(k[1] * 10)
                        ts, rs = '+' if t >= 0 else '-', '+' if r >= 0 else '-'
                        fname = f"Dist_T{ts}{abs(t):04d}_R{rs}{abs(r):04d}.json"
                        self.save_json(v, os.path.join(self.exam_folder, self.carm, 'calib_arcs', 'distortion', fname))
                    framecalib.pop('distortion')

                if 'gantry' in framecalib:
                    for k, v in framecalib['gantry'].items():
                        t, r = int(k[0] * 10), int(k[1] * 10)
                        ts, rs = '+' if t >= 0 else '-', '+' if r >= 0 else '-'
                        fname = f"Gant_T{ts}{abs(t):04d}_R{rs}{abs(r):04d}.json"
                        self.save_json(v, os.path.join(self.exam_folder, self.carm, 'calib_arcs', 'gantry', fname))
                    framecalib.pop('gantry')

                # remove/append to framedata
                framedata.pop('processed_frame')
                framedata['ShotIndex'] = self.shot_count
                framedata['analysis_parameters'] = analysis_parameters
                framedata['framecalib'] = framecalib
                # Save JSON with 'S' prefix
                json_filename = self.get_formatted_filename('S', data_type, self.shot_count) + '.json'
                json_path = os.path.join(self.exam_folder, 'shots', json_filename)
                self.save_json(framedata, json_path)

                self.shot_count += 1

            elif analysis_type == 'recon':
                m = {'hmplv1': 'hp1', 'hmplv2': 'hp2', 'acecup': 'cup', 'tothip': 'tri'}
                recon_result = data_for_exam
                data_type = recon_result.get('section', 'unknown')  # Get type or default to 'unknown'
                # Save recon with 'R' prefix
                recon_result['ReconIndex'] = self.recon_count
                json_filename = self.get_formatted_filename('R', m[data_type], self.recon_count) + '.json'
                json_path = os.path.join(self.exam_folder, 'recons', json_filename)
                self.save_json(recon_result, json_path)
                self.recon_count += 1

            elif analysis_type == 'reg':
                m = {'pelvis': 'hp2', 'regcup': 'cup', 'regtri': 'tri'}
                reg_result = data_for_exam
                data_type = reg_result.get('section', 'unknown')  # Get type or default to 'unknown'

                # Save stitch image with 'M' prefix
                stitch = reg_result.get('stitched_image')
                if stitch is not None:
                    stitch_filename = self.get_formatted_filename('M', m[data_type], self.reg_count) + '.png'
                    stitch_path = os.path.join(self.exam_folder, 'regs', stitch_filename)
                    os.makedirs(os.path.dirname(stitch_path), exist_ok=True)
                    cv2.imwrite(stitch_path, stitch)
                
                # Save JSON with 'M' prefix
                reg_result['RegIndex'] = self.reg_count
                json_filename = self.get_formatted_filename('M', m[data_type], self.reg_count) + '.json'
                json_path = os.path.join(self.exam_folder, 'regs', json_filename)
                
                # Remove stitch data before saving JSON
                reg_result.pop('stitched_image', None)  # Use pop with default to avoid KeyError
                self.save_json(reg_result, json_path)
                self.reg_count += 1
            
            # Ensure counter doesn't exceed 999
            if self.shot_count > 999:
                raise Exception("Maximum save count (999) exceeded")
        except Exception as e:
            self.bugs[0] = str(e)
            self.bugs.append(str(e))
            self.logger.error(f'Exception in {self.__class__.__name__}: {str(e)}')

    def save_patient(self, data):
        json_filename = 'patient.json'
        json_path = os.path.join(self.exam_folder, json_filename)
        self.save_json(data, json_path)