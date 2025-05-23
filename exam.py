import cv2
import os
import json

class Exam:
    def __init__(self):
        self.exam_folder = 'exam'
        self.shot_count = 0
        self.recon_count = 0
        self.reg_count = 0  
        
    def save_json(self, data, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    def get_formatted_filename(self, prefix, data_type, count):
        """Generate filename with format: [Prefix]-[Count]-[Type].extension"""
        count_str = f'{count:03d}'  # Format as 3-digit string with leading zeros
        return f"{prefix}-{count_str}-{data_type}"

    def save(self, dataforsave, image=None, rawframe=None):
        data_type = dataforsave.get('type', 'unknown')  # Get type or default to 'unknown'
        
        if dataforsave['folder'] == 'shots':
            # Save raw frame with 'W' prefix
            if rawframe is not None:
                raw_filename = self.get_formatted_filename('W', data_type, self.shot_count) + '.png'
                raw_path = os.path.join(self.exam_folder, 'shots/rawframes', raw_filename)
                os.makedirs(os.path.dirname(raw_path), exist_ok=True)
                cv2.imwrite(raw_path, rawframe)

            # Save shot with 'S' prefix
            if image is not None:
                shot_filename = self.get_formatted_filename('S', data_type, self.shot_count) + '.png'
                shot_path = os.path.join(self.exam_folder, 'shots', shot_filename)
                os.makedirs(os.path.dirname(shot_path), exist_ok=True)
                cv2.imwrite(shot_path, image)
                
            # Save JSON with 'S' prefix
            dataforsave['ShotIndex'] = self.shot_count
            json_filename = self.get_formatted_filename('S', data_type, self.shot_count) + '.json'
            json_path = os.path.join(self.exam_folder, 'shots', json_filename)
            self.save_json(dataforsave, json_path)

            self.shot_count += 1

        elif dataforsave['folder'] == 'recons':
            # Save recon with 'R' prefix
            dataforsave['ReconIndex'] = self.recon_count
            json_filename = self.get_formatted_filename('R', data_type, self.recon_count) + '.json'
            json_path = os.path.join(self.exam_folder, 'recons', json_filename)
            self.save_json(dataforsave, json_path)
            self.recon_count += 1

        elif dataforsave['folder'] == 'regs':
            # Save stitch image with 'M' prefix
            stitch = dataforsave.get('stitch')
            if stitch is not None:
                stitch_filename = self.get_formatted_filename('M', data_type, self.reg_count) + '.png'
                stitch_path = os.path.join(self.exam_folder, 'regs', stitch_filename)
                os.makedirs(os.path.dirname(stitch_path), exist_ok=True)
                cv2.imwrite(stitch_path, stitch)
            
            # Save JSON with 'M' prefix
            dataforsave['RegIndex'] = self.reg_count
            json_filename = self.get_formatted_filename('M', data_type, self.reg_count) + '.json'
            json_path = os.path.join(self.exam_folder, 'regs', json_filename)
            
            # Remove stitch data before saving JSON
            dataforsave.pop('stitch', None)  # Use pop with default to avoid KeyError
            self.save_json(dataforsave, json_path)
            self.reg_count += 1
        
        
        # Ensure counter doesn't exceed 999
        if self.shot_count > 999:
            raise Exception("Maximum save count (999) exceeded")