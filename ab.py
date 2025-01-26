import cv2
import numpy as np
import time
import threading
import json

class Shot:
    def __init__(self, stage, frame):
        self.stage=stage
        self.frame=frame
        self.view=None

class Recon:
    def __init__(self,label,shot1,shot2):
        self.label=label
        self.shot1=shot1
        self.shot2=shot2
        self.analysisdata=None

class AnalyzeBox:
    def __init__(self):
        self._stitch_progress = 0
        self._lock = threading.Lock()
        self._result = None
        self.images = [[None]*4, [None]*2, [None]*2]
        self.stitched_result = [None]*2
        self._is_processing = False
        self._stitch_thread = None
        self.mode = 1  # Default to normal mode
        self.shots=[Shot('HP1',1),Shot('HP1',2),Shot('HP2',1),Shot('HP2',2),Shot('CUP',1),Shot('CUP',2),Shot('TRI',1),Shot('TRI',2)]
        self.recons=[Recon('HP1',self.shots[0],self.shots[1]),Recon('HP2',self.shots[2],self.shots[3]),Recon('CUP',self.shots[4],self.shots[5]),Recon('TRI',self.shots[6],self.shots[7])]
        self.reference_calib={
            "RefHeader": {                
                "Labels": ['AP','RO','LO'],
                "ImuTilts": [3.0, 3.0, 3.0],
                "ImuRotations": [0.0, 0.0, 0.0]
            },
            "Reference": {}
        }
        self.distortion = [None]*4
        self.allresults={}

    @property
    def is_processing(self):
        """Returns whether the AnalyzeBox is currently processing (storing images or stitching)."""
        with self._lock:
            return self._is_processing

    @property
    def stitch_progress(self):
        """Returns the current progress (0-100) of the stitch operation."""
        with self._lock:
            return self._stitch_progress

    def analyze_phantom(self, current_stage, current_frame, image):
        try:
            distort = {'distort':[]}
            self.distortion[(current_stage//2)*2+current_frame-1] = distort
            if current_frame % 2 == 1:
                with open('reference_ap.json', 'r') as f:
                    camcalib = json.load(f)
            else:
                if current_frame == 2:
                    with open('reference_ro.json', 'r') as f:
                        camcalib = json.load(f)
                else:
                    with open('reference_lo.json', 'r') as f:
                        camcalib = json.load(f)

            for i in camcalib:
                self.reference_calib['Reference'][i] = camcalib[i]
            return True, (distort, self.reference_calib, image), None
        except Exception as e:
            return False, None, f"Error in analyze_phantom: {str(e)}"

    def analyze_landmark(self, current_stage, current_frame, view):
        try:
            with open('calcdata.json', 'r') as f:
                landmark = json.load(f)
            return True, landmark, None
        except Exception as e:
            return False, None, f"Error in analyze_landmark: {str(e)}"

    def can_recon(self):
        return True

    def reconstruct(self, stage, i):
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
            self._result = None
        
        try:
            result = self.stitch(self.images[0][i*2], self.images[0][i*2+1])
            self.stitched_result[i] = result
            idx=i if stage==1 else stage 
            self.recons[idx].analysisdata = result
            data = self.recons[idx]
            return True, (result, data), None
        except Exception as e:
            return False, None, f"Error in reconstruct: {str(e)}"
        finally:
            with self._lock:
                self._is_processing = False

    def analyzeref(self):
        try:
            self.allresults={
                "OperativeSide": "R",
                "Reference":{
                    "ReconIndex1": 0,
                    "ReconIndex2": 1,
                    "Measurements":{
                        "PelvicTilt": 0.0,
                        "PelvicRotation": 0.0,
                        "PelvicAnttilt": 0.0,
                        "FemurFlex": 0.0,
                        "FemurAbd": 0.0,
                        "FemurRot": 0.0
                    }
                }
            }
            return True, self.allresults, None
        except Exception as e:
            return False, None, f"Error in analyzeref: {str(e)}"


    def analyzecup(self):
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
        try:
            # Check for required data
            if self.recons[2].analysisdata is None:
                return False, None, "Reconstruction result from stage 3 is missing"
            
            if "Reference" not in self.allresults:
                return False, None, f"Reference analysis result is missing"
            
            self.allresults["CupAnalysis"] = {
                "ReconIndex": 2,
                "Measurements": 0,
                "CupInclination": 0,
                "CupAntversion": 0
            }
        
            if self.images[1][0] is not None and self.images[1][1] is not None:
                result = self.stitch(self.images[1][0], self.images[1][1])
                return True, (result, self.allresults), None
            return False, None, "Missing images for cup analysis"
        except Exception as e:
            return False, None, str(e)
        finally:
            with self._lock:
                self._is_processing = False


    def analyzetrial(self):
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
        try:
            # Check for required data
            if self.recons[3].analysisdata is None:
                return False, None, "Reconstruction result from stage 3 is missing"
            
            if "Reference" not in self.allresults:
                return False, None, f"Reference analysis result is missing"

            self.allresults["TrialAnalysis"] = {
                "ReconIndex": 3,
                "Measurements": 0,
                "LLD": 0,
                "Offset": 0
            }
            
            if self.images[2][0] is not None and self.images[2][1] is not None:
                result = self.stitch(self.images[2][0], self.images[2][1])
                return True, (result, self.allresults), None
            return False, None, "Missing images for trial analysis"
        except Exception as e:
            return False, None, str(e)
        finally:
            with self._lock:
                self._is_processing = False

    def analyzeframe(self, current_stage, current_frame, frame_or_dict, calib_data, target_size=700):
        """
        Analyze and store a single frame.
        
        Returns:
        - True, cropped_and_rotated_image, None: If successful (rotation <= 20)
        - False, cropped_image, "Glyph error: rotation exceeds 20 degrees": If rotation > 20
        - False, None, error_message: If any other error occurs
        """
        try:
            frame_img = frame_or_dict
            
            # Get cropping information from calibration data
            crop_top_left = calib_data['FrameGrabber']['CropTopLeft']
            crop_size = calib_data['FrameGrabber']['CropSize']
            rotation_angle = calib_data['FrameGrabber']['GlyphRefRotation']
            
            # Crop the image
            start_x, start_y = crop_top_left
            width, height = crop_size
            cropped = frame_img[start_y:start_y+height, start_x:start_x+width]
            
            # Check rotation angle
            if abs(rotation_angle) > 20:
                # Return cropped image with glyph error message if rotation exceeds 20 degrees
                return False, cropped, "Glyph error: rotation exceeds 20 degrees"
            
            # Rotate the image if angle is not zero
            if rotation_angle != 0:
                (h, w) = cropped.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, -rotation_angle, 1.0)  # Negative angle for clockwise rotation
                cropped = cv2.warpAffine(cropped, M, (w, h))
            
            # Store the processed image
            self.images[current_stage-1][current_frame-1] = cropped
            return True, cropped, None
            
        except Exception as e:
            return False, None, str(e)

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
                    self._stitch_progress = (k + 1) /300000
                    k+=1

        # Stitch the images
        self._result = np.hstack((frame1_resized, frame2_resized))
        return self._result

    def adjust_brightness(self, image, brightness_adjustment):
        """
        Adjust the brightness of an image.
        
        Parameters:
        image: numpy array of the input image
        brightness_adjustment: int between -100 and 100
        
        Returns:
        numpy array of the adjusted image
        """
        # Ensure brightness_adjustment is in the valid range
        brightness_adjustment = max(-100, min(brightness_adjustment, 100))
        
        # Map brightness_adjustment from [-100, 100] to [-127, 127]
        beta = int(brightness_adjustment * 1.27)
        
        # Use cv2.convertScaleAbs to adjust brightness
        adjusted = cv2.convertScaleAbs(image, alpha=1, beta=beta)
        return adjusted
        