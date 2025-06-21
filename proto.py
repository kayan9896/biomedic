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
panel = None
config = ConfigManager()
server_lock = threading.Lock()


def frontend_to_backend_coords(coords, backend_size=1024, frontend_size=960, flip_horizontal=False):
    """
    Convert coordinates from frontend (960x960) to backend (1024x1024) scale
    
    Args:
        coords: Can be a single [x,y] coordinate pair or nested structures containing coordinates
        backend_size: Size of the backend image (default 1024)
        frontend_size: Size of the frontend display (default 960)
        flip_horizontal: If True, will flip x-coordinates horizontally (mirror effect)
    
    Returns:
        Converted coordinates in the same structure as input
    """
    scale_factor = backend_size / frontend_size
    
    if isinstance(coords, list):
        if len(coords) == 2 and all(isinstance(c, (int, float)) for c in coords):
            # Single [x,y] coordinate pair
            x, y = coords
            
            # Scale the coordinates
            x_scaled = x * scale_factor
            y_scaled = y * scale_factor
            
            # Flip horizontally if requested
            if flip_horizontal:
                x_scaled = backend_size - x_scaled
                
            return [int(x_scaled), int(y_scaled)]
        else:
            # Nested list structure
            return [frontend_to_backend_coords(item, backend_size, frontend_size, flip_horizontal) for item in coords]
    elif isinstance(coords, dict):
        # Dictionary structure
        return {k: frontend_to_backend_coords(v, backend_size, frontend_size, flip_horizontal) for k, v in coords.items()}
    else:
        # Return non-coordinate values unchanged
        return coords

def backend_to_frontend_coords(coords, backend_size=1024, frontend_size=960, flip_horizontal=False):
    """
    Convert coordinates from backend (1024x1024) to frontend (960x960) scale
    
    Args:
        coords: Can be a single [x,y] coordinate pair or nested structures containing coordinates
        backend_size: Size of the backend image (default 1024)
        frontend_size: Size of the frontend display (default 960)
        flip_horizontal: If True, will flip x-coordinates horizontally (mirror effect)
    
    Returns:
        Converted coordinates in the same structure as input
    """
    scale_factor = frontend_size / backend_size
    
    if isinstance(coords, list):
        if len(coords) == 2 and all(isinstance(c, (int, float)) for c in coords):
            # Single [x,y] coordinate pair
            x, y = coords
            
            # Flip horizontally if requested
            if flip_horizontal:
                x = backend_size - x
                
            # Scale the coordinates
            x_scaled = x * scale_factor
            y_scaled = y * scale_factor
            
            return [int(x_scaled), int(y_scaled)]
        else:
            # Nested list structure
            return [backend_to_frontend_coords(item, backend_size, frontend_size, flip_horizontal) for item in coords]
    elif isinstance(coords, dict):
        # Dictionary structure
        return {k: backend_to_frontend_coords(v, backend_size, frontend_size, flip_horizontal) for k, v in coords.items()}
    else:
        # Return non-coordinate values unchanged
        return coords

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
        
carm_folder = config.get("carm_folder", "./Calibration")
carm_data = {}
select = {}
@app.route('/get-carms', methods=['GET'])
def get_carms():
    """Endpoint to retrieve C-arm data from JSON file"""
    
    try:
        for name in os.listdir(carm_folder):
            carm_data[name] = {'image': f"http://localhost:5000/carm-images/{name}"}
        
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

        image = cv2.imread(f"{carm_folder}/{filename}/carm_photo.png")
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({
            'image': f'data:image/jpeg;base64,{image_base64}'
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
    if panel is None: panel = Panel(config)
    with server_lock:
        if controller is None:
            controller = Controller(FrameGrabber(), Model(), config, select, panel)
        
        # Get the connection result
        result = controller.connect_video()
        
        # If connection successful, try to get the first frame
        if result.get('connected', False):
            try:
                # Wait a brief moment for the video to stabilize
                time.sleep(0.5)
                
                # Fetch the first frame
                frame = controller.frame_grabber.fetchFrame()
                
                if frame is not None:
                    # Convert numpy array to JPEG
                    retval, buffer = cv2.imencode('.jpg', frame)
                    
                    if retval:
                        # Convert to base64
                        jpg_bytes = buffer.tobytes()
                        base64_str = base64.b64encode(jpg_bytes).decode('utf-8')
                        
                        # Add the frame to the result as a data URI
                        result['frame'] = f"data:image/jpeg;base64,{base64_str}"
                    else:
                        controller.logger.warning("Failed to encode frame to JPEG")
                else:
                    controller.logger.warning("No frame available after connection")
                    
            except Exception as e:
                controller.logger.error(f"Error getting initial frame: {str(e)}")
                # Still return success but without the frame
                pass
        
        return jsonify(result)

@app.route('/check-tilt-sensor', methods=['GET'])
def check_tilt_sensor():
    """Endpoint to check tilt sensor status using actual IMU values"""
    global controller
    
    with server_lock:
        if controller is None:
            controller = Controller(FrameGrabber(), Model(), config)
        
        # Get IMU connection status and battery level
        is_connected = False
        battery_level = 100
        
        if hasattr(controller, 'imu'):
            is_connected = getattr(controller.imu, 'is_connected', False)
            battery_level = getattr(controller.imu, 'battery_level', 100)
        
        # Determine battery_low status
        battery_low = battery_level <= 20
        
        if not is_connected:
            message = "Tilt sensor disconnected. Please check the connection."
        elif battery_low:
            message = "Tilt sensor connected but battery is low. Consider replacing batteries soon."
        else:
            message = "Tilt sensor connected successfully."
        
        return jsonify({
            "connected": is_connected,
            "battery_low": battery_low,
            "message": message
        })
        
@app.route('/run2', methods=['POST'])
def start_processing2():
    """Start video capture and frame processing"""
    global controller
    
    with server_lock:
        if controller is None:
            controller = Controller(FrameGrabber(), Model(), config)
        
        if controller.is_running:
            return jsonify({"error": "Processing is already running"}), 400
        
        # Connect to the video device and start processing
        result = controller.run2()
        if isinstance(result, str):
            return jsonify({"error": result}), 500
        
        return jsonify({"message": f"Started processing on device"})

@app.route('/api/states')
def get_states():
    global controller
    if controller is None:
            controller = Controller(FrameGrabber(), Model())
    
    return jsonify(controller.get_states())

@app.route('/api/setting', methods=['POST'])
def set_ai_mode():
    global controller
    if controller is None:
        controller = Controller(FrameGrabber(), Model())
    
    try:
        data = request.get_json()
        if 'ai_mode' in data:
            ai_mode = data.get('ai_mode', True)
            controller.ai_mode = ai_mode
            controller.model.ai_mode = ai_mode
        if 'autocollect' in data:
            autocollect = data.get('autocollect', True)
            controller.autocollect = autocollect
        if 'tracking' in data:
            tracking = data.get('tracking', True)
            controller.tracking = tracking

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/image-with-metadata')
def get_image_with_metadata():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    
    image_data = controller.get_image_with_metadata()
    
    if image_data['image'] is None:
        return jsonify({"error": "No image available"}), 404
    
    # Convert the image to base64 encoding
    _, buffer = cv2.imencode('.jpg', image_data['image'])
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Convert metadata coordinates from backend to frontend scale
    converted_metadata = backend_to_frontend_coords(image_data['metadata'])
    
    # Return both image and converted metadata in JSON
    return jsonify({
        'image': f'data:image/jpeg;base64,{image_base64}',
        'metadata': converted_metadata,
        'checkmark': image_data['checkmark'],
        'recon': image_data['recon'],
        'error': image_data['error'],
        'next': image_data['next'],
        'measurements': image_data['measurements'],
        'side': image_data['side']
    })

@app.route('/landmarks', methods=['POST'])
def landmarks():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    stage = request.json.get('stage')
    
    # Convert landmarks from frontend to backend scale
    l = request.json.get('leftMetadata')
    r = request.json.get('rightMetadata')
    limgside = request.json.get('limgside')
    rimgside = request.json.get('rimgside')
    
    converted_l = frontend_to_backend_coords(l) if l else None
    # Apply horizontal flipping for right metadata
    converted_r = frontend_to_backend_coords(r, flip_horizontal=False) if r else None
    
    controller.update_landmarks(converted_l, converted_r, limgside, rimgside, stage)
    
    return jsonify({"message": "update landmarks"})


@app.route('/cap', methods=['POST'])
def cap():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    state = request.json.get('cap')
    controller.do_capture = state
    return jsonify({"message": "do capture"})

@app.route('/label', methods=['POST'])
def label():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    label = request.json.get('label')
    controller.viewmodel.states['active_side'] = label
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

    controller.uistates = state
    controller.viewmodel.states['stage'] = stage
    if controller.imu: controller.imu.confirm_save()

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
    
    # Create directory if it doesn't exist
    save_dir = f'{controller.exam.exam_folder}/viewpairs'
    os.makedirs(save_dir, exist_ok=True)
    
    # Save the file
    filename = f'screenshot{stage}.png'
    file_path = os.path.join(save_dir, filename)
    file.save(file_path)
    
    image = Image.open(file)
    image_array = np.array(image)
    controller.model.viewpairs[stage] = image_array
    print(controller.model.viewpairs[stage])
    
    return jsonify({"message": f"screenshot saved successfully"})

@app.route('/screenshot/<int:stage>')
def get_screen(stage):
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    
    stitch = controller.model.viewpairs[stage]
    
    if stitch is None:
        return jsonify({
        'img': None,
        })
    
    # Convert the image to base64 encoding
    _, buffer = cv2.imencode('.jpg', stitch)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Return both image and metadata in JSON
    return jsonify({
        'img': f'data:image/jpeg;base64,{image_base64}',
    })

@app.route('/stitch/<int:stage>')
def get_stitch(stage):
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    
    
    if stage < 2:
        stitch = controller.model.data['pelvis']['stitch']
    if stage == 2:
        stitch = controller.model.data['regcup']['stitch']
    if stage == 3:
        stitch = controller.model.data['regtri']['stitch']
    
    if stitch is None:
        return jsonify({
        'img': None,
        })
    
    # Convert the image to base64 encoding
    _, buffer = cv2.imencode('.jpg', stitch)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Return both image and metadata in JSON
    return jsonify({
        'img': f'data:image/jpeg;base64,{image_base64}',
    })

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
