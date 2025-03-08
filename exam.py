import cv2
import os
import json

class Exam:
    def __init__(self):
        self.exam_folder = 'exam'
        self.shot_ct = 0
        self.recon_ct = 0
        self.reg_ct = 0
        
    def save_json(self, data, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def save(self, dataforsave, image=None, rawframe=None):
        if dataforsave['folder'] == 'shots':
            if rawframe is not None:
                raw_path = os.path.join(self.exam_folder, 'shots/rawframes', f'{self.shot_ct}.png')
                os.makedirs(os.path.dirname(raw_path), exist_ok=True)
                cv2.imwrite(raw_path, rawframe)

            if image is not None:
                shot_path = os.path.join(self.exam_folder, 'shots', f'shot{self.shot_ct}.png')
                os.makedirs(os.path.dirname(shot_path), exist_ok=True)
                cv2.imwrite(shot_path, image)
                

            json_path = f'shots/shot{self.shot_ct}.json'
            self.save_json(dataforsave, os.path.join(self.exam_folder, json_path))
            self.shot_ct += 1

        if dataforsave['folder'] == 'recons':
            json_path = f'recons/recon{self.recon_ct}.json'
            self.save_json(dataforsave, os.path.join(self.exam_folder, json_path))
            self.recon_ct += 1

        if dataforsave['folder'] == 'regs':
            stitch = dataforsave['stitch']
            if stitch is not None:
                stitch_path = f'regs/stitch{self.reg_ct}.png'
                os.makedirs(os.path.dirname(os.path.join(self.exam_folder, stitch_path)), exist_ok=True)
                cv2.imwrite(os.path.join(self.exam_folder, stitch_path), stitch)
            json_path = f'regs/reg{self.reg_ct}.json'
            dataforsave.pop('stitch')
            self.save_json(dataforsave, os.path.join(self.exam_folder, json_path))
            self.reg_ct += 1
