from flask import Flask, jsonify, request, Response, send_from_directory
import cv2
import threading
import io
from PIL import Image
import time
from model import Model
from fg import FrameGrabber
from controller import Controller
from config_manager import ConfigManager
from calibrate import Calibrate
from panel import Panel
from flask_cors import CORS
import numpy as np
import json
import base64

import logging
from logging.handlers import RotatingFileHandler
import os

class Filter(logging.Filter):
    def filter(self, record):  
        return "api/states" not in record.getMessage()

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up the logger
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)  # Set the logging level
    logger.addFilter(Filter())
    
    # Create a file handler
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Call this function at the start of your script
setup_logging()

app = Flask(__name__)
CORS(app)

#app.logger.setLevel(logging.DEBUG)

# Global variables
frame_grabber = None
analyze_box = None
controller = None

config = ConfigManager()
calibrate = Calibrate()
panel = Panel(config) if config.get('on_simulation') else None
server_lock = threading.Lock()


carm_folder = config.get("carm_folder", "./Calibration")
select = {}
@app.route('/get-carms', methods=['GET'])
def get_carms():
    """Endpoint to retrieve C-arm data from JSON file"""
    global panel
    global controller
    if panel and panel.jumpped:
        controller = panel.controller
        return jsonify({'jump': True})
    try:
        carm_data = calibrate.get_carms(carm_folder)
        return jsonify(carm_data)
    except Exception as e:
        print(f"Error fetching C-arm data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/carm-images/<filename>', methods=['GET'])
def serve_carm_image(filename):
    """Endpoint to serve C-arm images"""
    global select
    global controller
    if controller: 
        controller = None
    try:
        select = calibrate.serve_carm_select(carm_folder, filename)
        image_base64 = calibrate.serve_carm_image(carm_folder, filename)
        
        return jsonify({
            'image': f'data:image/jpeg;base64,{image_base64}',
            'imu_on': select['IMU']['imu_on']
        })
    except Exception as e:
        print(f"Error serving image {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 404


@app.route('/check-video-connection', methods=['GET'])
def check_video_connection():
    """Endpoint to simulate checking video connection"""
    global controller
    global select
    global panel

    with server_lock:
        if controller is None:
            controller = Controller(config, select, panel)
        
        # Get the connection result
        result = controller.connect_video()
        
        return jsonify(result)

@app.route('/check-tilt-sensor', methods=['GET'])
def check_tilt_sensor():
    """Endpoint to check tilt sensor status using actual IMU values"""
    global controller
    
    with server_lock:
        if controller is None:
            controller = Controller(config)
        
        return jsonify(controller.imu_sensor.check_tilt_sensor())
        
@app.route('/run2', methods=['POST'])
def start_processing():
    """Start video capture and frame processing"""
    global controller
    
    with server_lock:
        if controller is None:
            controller = Controller(config)

        # Connect to the video device and start processing
        result = controller.start_processing()
        if not result:
            return jsonify({"error": "Processing is already running"}), 400
        
        return jsonify({"message": f"Started processing on device"})

@app.route('/api/states')
def get_states():
    global controller
    try:
        return jsonify(controller.get_states())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/setting', methods=['POST'])
def set_ai_autocollect_modes():
    global controller
    if controller is None:
        controller = Controller()
    
    try:
        data = request.get_json()
        controller.set_ai_autocollect_modes(data)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/image-with-metadata')
def get_image_with_metadata():
    try:
        global controller
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        
        image_data = controller.get_image_with_metadata()
        
        # Return both image and converted metadata in JSON
        return jsonify(image_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/landmarks', methods=['POST'])
def save_landmarks():
    try:
        global controller
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        
        stage = request.json.get('stage')
        l = request.json.get('leftMetadata')
        r = request.json.get('rightMetadata')
        limgside = request.json.get('limgside')
        rimgside = request.json.get('rimgside')
        
        controller.update_landmarks(l, r, limgside, rimgside, stage)
        
        return jsonify({"message": "update landmarks"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/cap', methods=['POST'])
def manual_framecap():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    state = request.json.get('cap')
    controller.do_capture = state
    return jsonify({"message": "do capture"})

@app.route('/label', methods=['POST'])
def switch_side():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    label = request.json.get('label')
    controller.active_side = label
    return jsonify({"message": "click label switch active side"})
    
@app.route('/edit', methods=['POST'])
def edit():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    state = request.json.get('uistates')
    controller.pause_states = state
    return jsonify({"message": "pause_states updated"})

@app.route('/next', methods=['POST'])
def next():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    state = request.json.get('uistates')
    stage = request.json.get('stage')
    controller.next(state, stage)

    return jsonify({"message": "uistates updated"})

@app.route('/restart', methods=['POST'])
def restart():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    controller.restart()

    return jsonify({"message": "uistate restart"})

@app.route('/screenshot/<int:stage>', methods=['POST'])
def save_screen(stage):
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404

    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    controller.save_screen(stage, file)
    
    return jsonify({"message": f"screenshot saved successfully"})

@app.route('/screenshot/<int:stage>')
def get_screen(stage):
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    
    return jsonify(controller.get_screen(stage))

@app.route('/stitch/<int:stage>')
def get_stitch(stage):
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    
    return jsonify(controller.get_stitch(stage))

@app.route('/patient', methods=['POST'])
def patient():
    try:
        global controller
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404

        controller.patient(request.get_json())

        return jsonify({"message": f"patient saved successfully"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

'''
@app.route('/check-running-state', methods=['GET'])
def check_running_state():
    """Check if controller is running and return necessary state data including all image data"""
    global controller
    
    with server_lock:
        if controller is None or not controller.is_running:
            return jsonify({"running": False})
        
        # Get basic states
        states = controller.get_states()
        current_stage_idx = states.get('stage', 0)
        
        # Determine which data keys to check based on current stage
        stage_data_mapping = {
            0: ['hp1-ap', 'hp1-ob'],
            1: ['hp2-ap', 'hp2-ob'],
            2: ['cup-ap', 'cup-ob'],
            3: ['tri-ap', 'tri-ob']
        }
        
        # Create a map of all stage data to check the full state
        all_stage_data = {}
        for stage_idx, keys in stage_data_mapping.items():
            all_stage_data[stage_idx] = {
                'ap_key': keys[0],
                'ob_key': keys[1],
                'ap_has_data': False,
                'ob_has_data': False,
                'ap_image': None,
                'ob_image': None,
                'ap_metadata': None,
                'ob_metadata': None,
                'ap_checkmark': None,
                'ob_checkmark': None,
                'ap_side': None,
                'ob_side': None
            }
            
            # Check if this stage has valid data
            ap_data = controller.model.data.get(keys[0], {})
            ob_data = controller.model.data.get(keys[1], {})
            
            # Determine if each side has valid data
            ap_has_data = ap_data.get('image') is not None 
            ob_has_data = ob_data.get('image') is not None 
            
            # Store the evaluation results
            all_stage_data[stage_idx]['ap_has_data'] = ap_has_data
            all_stage_data[stage_idx]['ob_has_data'] = ob_has_data
            
            # Only prepare image data if the side has valid data
            if ap_has_data:
                _, buffer = cv2.imencode('.jpg', ap_data['image'])
                all_stage_data[stage_idx]['ap_image'] = f'data:image/jpeg;base64,{base64.b64encode(buffer).decode("utf-8")}'
                all_stage_data[stage_idx]['ap_metadata'] = backend_to_frontend_coords(ap_data.get('metadata', {})) if ap_data.get('metadata') else None
                all_stage_data[stage_idx]['ap_side'] = ap_data.get('side')
            
            if ob_has_data:
                _, buffer = cv2.imencode('.jpg', ob_data['image'])
                all_stage_data[stage_idx]['ob_image'] = f'data:image/jpeg;base64,{base64.b64encode(buffer).decode("utf-8")}'
                all_stage_data[stage_idx]['ob_metadata'] = backend_to_frontend_coords(ob_data.get('metadata', {})) if ob_data.get('metadata') else None
                all_stage_data[stage_idx]['ob_side'] = ob_data.get('side')
        
        # Get viewmodel data for current AP and OB
        ap_viewmodel = controller.viewmodel.imgs[0] if all_stage_data[current_stage_idx]['ap_has_data'] else {}
        ob_viewmodel = controller.viewmodel.imgs[1] if all_stage_data[current_stage_idx]['ob_has_data'] else {}
        
        # Get current stage data
        current_stage_data = all_stage_data.get(current_stage_idx, {})
        
        # Add checkmarks from viewmodel for the current stage
        if current_stage_data:
            current_stage_data['ap_checkmark'] = ap_viewmodel.get('checkmark')
            current_stage_data['ob_checkmark'] = ob_viewmodel.get('checkmark')
        
        # Get error messages
        ap_error = ap_viewmodel.get('error') if ap_viewmodel else None
        ob_error = ob_viewmodel.get('error') if ob_viewmodel else None
        
        # Check if we should move to next stage
        move_next = (ap_viewmodel.get('next', False) or ob_viewmodel.get('next', False))
        
        # Get measurements data
        measurements = None
        # Check the relevant section for the current stage
        stage_measurement_mapping = {
            1: 'pelvis',
            2: 'regcup',
            3: 'regtri'
        }
        
        if current_stage_idx in stage_measurement_mapping:
            section_data = controller.model.data.get(stage_measurement_mapping[current_stage_idx], {})
            if section_data.get('success'):
                measurements = section_data.get('RegsResult', None)
        
        return jsonify({
            "running": True,
            "states": states,
            "current_stage": controller.current_stage,  # 0-indexed for frontend
            "all_stage_data": all_stage_data,
            "move_next": move_next,
            "tilt_angle": states.get('tilt_angle', 0),
            "rotation_angle": states.get('rotation_angle', 0),
            "ap_rotation_angle": getattr(controller, 'ap_rotation_angle', None),
            "ob_rotation_angle": getattr(controller, 'ob_rotation_angle', None),
            "ob_rotation_angle2": getattr(controller, 'ob_rotation_angle2', None),
            "target_tilt_angle": getattr(controller, 'target_tilt_angle', None),
            "measurements": measurements,
            "error": ap_error or ob_error
        })
'''

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
