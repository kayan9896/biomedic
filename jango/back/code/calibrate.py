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
        if not self.verify_config(select)[0]: raise Exception('Wrong calib data')

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
    
    def verify_config(self, config):
        """
        Verifies the structure, data types, and constraints of a configuration dictionary.
        Ensures CarmTargetTilt and CarmTargetRot adhere to range logic.
        Returns a tuple (is_valid, errors) where is_valid is a boolean and errors is a list of error messages.
        """
        errors = []

        # Check if config is a dictionary
        if not isinstance(config, dict):
            errors.append("Config must be a dictionary")
            return False, errors

        # Required top-level keys
        required_keys = {"Carm", "FrameGrabber", "IMU", "Model"}
        if not all(key in config for key in required_keys):
            errors.append(f"Config must contain all required keys: {required_keys}")
            return False, errors

        # Validate Carm section
        if not isinstance(config["Carm"], dict):
            errors.append("Carm must be a dictionary")
        else:
            if not all(key in config["Carm"] for key in ["C-arm Model", "C-arm Manufacturer"]):
                errors.append("Carm must contain keys: 'C-arm Model', 'C-arm Manufacturer'")
            else:
                if not isinstance(config["Carm"]["C-arm Model"], str):
                    errors.append("Carm.C-arm Model must be a string")
                if not isinstance(config["Carm"]["C-arm Manufacturer"], str):
                    errors.append("Carm.C-arm Manufacturer must be a string")

        # Validate IMU section
        if not isinstance(config["IMU"], dict):
            errors.append("IMU must be a dictionary")
        else:
            required_imu_keys = {
                "DeviceName", "PortName", "Baudrate", "ReadFrequency",
                "MinBatteryVolts", "MaxBatteryVolts", "ImuCalibMatrix",
                "ResetRotation", "ResetTilt", "ApplyTarget", "CarmRangeTilt",
                "CarmRangeRotation", "CarmTargetTilt", "CarmTargetRot", "tol", "imu_on"
            }
            if not all(key in config["IMU"] for key in required_imu_keys):
                errors.append(f"IMU must contain keys: {required_imu_keys}")
            else:
                if not isinstance(config["IMU"]["DeviceName"], str):
                    errors.append("IMU.DeviceName must be a string")
                if not isinstance(config["IMU"]["PortName"], str):
                    errors.append("IMU.PortName must be a string")
                if not isinstance(config["IMU"]["Baudrate"], int) or config["IMU"]["Baudrate"] <= 0:
                    errors.append("IMU.Baudrate must be a positive integer")
                if not isinstance(config["IMU"]["ReadFrequency"], (int, float)) or config["IMU"]["ReadFrequency"] <= 0:
                    errors.append("IMU.ReadFrequency must be a positive number")
                if not isinstance(config["IMU"]["MinBatteryVolts"], (int, float)) or config["IMU"]["MinBatteryVolts"] < 0:
                    errors.append("IMU.MinBatteryVolts must be a non-negative number")
                if not isinstance(config["IMU"]["MaxBatteryVolts"], (int, float)) or config["IMU"]["MaxBatteryVolts"] <= config["IMU"]["MinBatteryVolts"]:
                    errors.append("IMU.MaxBatteryVolts must be a number greater than MinBatteryVolts")
                if not isinstance(config["IMU"]["ImuCalibMatrix"], list) or len(config["IMU"]["ImuCalibMatrix"]) != 4:
                    errors.append("IMU.ImuCalibMatrix must be a list of 4 elements")
                else:
                    for i, row in enumerate(config["IMU"]["ImuCalibMatrix"]):
                        if not isinstance(row, list):
                            errors.append(f"IMU.ImuCalibMatrix[{i}] must be a list")
                if not isinstance(config["IMU"]["ResetRotation"], (int, float)):
                    errors.append("IMU.ResetRotation must be a number")
                if not isinstance(config["IMU"]["ResetTilt"], (int, float)):
                    errors.append("IMU.ResetTilt must be a number")
                if not isinstance(config["IMU"]["ApplyTarget"], bool):
                    errors.append("IMU.ApplyTarget must be a boolean")
                
                # Validate CarmRangeTilt
                if not isinstance(config["IMU"]["CarmRangeTilt"], list) or len(config["IMU"]["CarmRangeTilt"]) != 2:
                    errors.append("IMU.CarmRangeTilt must be a list of 2 numbers")
                else:
                    for i, val in enumerate(config["IMU"]["CarmRangeTilt"]):
                        if not isinstance(val, (int, float)):
                            errors.append(f"IMU.CarmRangeTilt[{i}] must be a number")
                    if len(config["IMU"]["CarmRangeTilt"]) == 2 and config["IMU"]["CarmRangeTilt"][0] > config["IMU"]["CarmRangeTilt"][1]:
                        errors.append("IMU.CarmRangeTilt[0] must be less than or equal to CarmRangeTilt[1]")

                # Validate CarmRangeRotation
                if not isinstance(config["IMU"]["CarmRangeRotation"], list) or len(config["IMU"]["CarmRangeRotation"]) != 4:
                    errors.append("IMU.CarmRangeRotation must be a list of 4 numbers")
                else:
                    for i, val in enumerate(config["IMU"]["CarmRangeRotation"]):
                        if not isinstance(val, (int, float)):
                            errors.append(f"IMU.CarmRangeRotation[{i}] must be a number")
                    if len(config["IMU"]["CarmRangeRotation"]) == 4:
                        if not (config["IMU"]["CarmRangeRotation"][0] <= config["IMU"]["CarmRangeRotation"][1] <=
                                config["IMU"]["CarmRangeRotation"][2] <= config["IMU"]["CarmRangeRotation"][3]):
                            errors.append("IMU.CarmRangeRotation must be in ascending order")

                # Validate CarmTargetTilt
                if config["IMU"]["CarmTargetTilt"] is not None:
                    if not isinstance(config["IMU"]["CarmTargetTilt"], (int, float)):
                        errors.append("IMU.CarmTargetTilt must be a number or null")
                    elif len(config["IMU"]["CarmRangeTilt"]) == 2:
                        min_tilt, max_tilt = config["IMU"]["CarmRangeTilt"]
                        if not (min_tilt <= config["IMU"]["CarmTargetTilt"] <= max_tilt):
                            errors.append(f"IMU.CarmTargetTilt must be within CarmRangeTilt [{min_tilt}, {max_tilt}]")

                # Validate CarmTargetRot
                if not isinstance(config["IMU"]["CarmTargetRot"], list) or len(config["IMU"]["CarmTargetRot"]) != 3:
                    errors.append("IMU.CarmTargetRot must be a list of 3 elements")
                else:
                    all_none = all(x is None for x in config["IMU"]["CarmTargetRot"])
                    all_values = all(isinstance(x, (int, float)) for x in config["IMU"]["CarmTargetRot"])
                    if not (all_none or all_values):
                        errors.append("IMU.CarmTargetRot must be all null or all numbers")
                    elif all_values and len(config["IMU"]["CarmRangeRotation"]) == 4:
                        rot_ranges = config["IMU"]["CarmRangeRotation"]
                        if not (rot_ranges[1] <= config["IMU"]["CarmTargetRot"][0] <= rot_ranges[2]):
                            errors.append(f"IMU.CarmTargetRot[0] must be within [{rot_ranges[1]}, {rot_ranges[2]}]")
                        if not (rot_ranges[0] <= config["IMU"]["CarmTargetRot"][1] <= rot_ranges[1]):
                            errors.append(f"IMU.CarmTargetRot[1] must be within [{rot_ranges[0]}, {rot_ranges[1]}]")
                        if not (rot_ranges[2] <= config["IMU"]["CarmTargetRot"][2] <= rot_ranges[3]):
                            errors.append(f"IMU.CarmTargetRot[2] must be within [{rot_ranges[2]}, {rot_ranges[3]}]")

                if not isinstance(config["IMU"]["tol"], (int, float)) or config["IMU"]["tol"] < 0:
                    errors.append("IMU.tol must be a non-negative number")
                if not isinstance(config["IMU"]["imu_on"], bool):
                    errors.append("IMU.imu_on must be a boolean")


        return len(errors) == 0, errors