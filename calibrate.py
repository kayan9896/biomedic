import json
import os
import cv2
import base64
from typing import Dict, Any, Optional

class Calibrate:
    def get_carms(self, carm_folder):
        carm_data = {}
        for name in os.listdir(carm_folder):
            carm_data[name] = {'image': f"http://localhost:5000/carm-images/{name}"}
        return carm_data

    def serve_carm_select(self, carm_folder, filename):
        with open(f"{carm_folder}/{filename}/hardware.json", 'r') as file:
            select = json.load(file)

        distortion = {}
        for fname in os.listdir(f"{carm_folder}/{filename}/calib_arcs/distortion"):
            with open(f"{carm_folder}/{filename}/calib_arcs/distortion/{fname}", 'r') as file:
                t = int(fname[6 : 11]) / 10
                r = int(fname[-10 : -5]) / 10
                distortion[(t,r)] = json.load(file)

        gantry = {}
        for fname in os.listdir(f"{carm_folder}/{filename}/calib_arcs/gantry"):
            with open(f"{carm_folder}/{filename}/calib_arcs/gantry/{fname}", 'r') as file:
                t = int(fname[6 : 11]) / 10
                r = int(fname[-10 : -5]) / 10
                gantry[(t,r)] = json.load(file)
        
        select.update({'distortion': distortion})
        select.update({'gantry': gantry})
        select.update({'folder': f"{carm_folder}/{filename}"})

        return select

    def serve_carm_image(self, carm_folder, filename):
        image = cv2.imread(f"{carm_folder}/{filename}/carm_photo.png")
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8') 

        return image_base64