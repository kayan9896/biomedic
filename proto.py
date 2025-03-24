from flask import Flask, jsonify, request, Response
import cv2
import threading
import io
from PIL import Image
import time
from ab2 import AnalyzeBox
from fg import FrameGrabber
from be2 import ImageProcessingController
from flask_cors import CORS
import numpy as np

import logging
from logging.handlers import RotatingFileHandler
import os

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the logging level
    
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
server_lock = threading.Lock()


from flask import send_file
from io import BytesIO
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

@app.route('/run2', methods=['POST'])
def start_processing2():
    """Start video capture and frame processing"""
    global controller
    
    with server_lock:
        if controller is None:
            controller = ImageProcessingController(FrameGrabber(), AnalyzeBox())
        
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
            controller = ImageProcessingController(FrameGrabber(), AnalyzeBox())
    
    return jsonify(controller.get_states())

import base64
@app.route('/api/image-with-metadata')
def get_image_with_metadata():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    
    angle = controller.viewmodel.states['rotation_angle']
    
    # Determine which image data to send
    if -15 <= angle <= 15:
        image_data = controller.viewmodel.imgs[0]
    elif -45 <= angle <= 45:
        image_data = controller.viewmodel.imgs[1]
    else:
        return jsonify({"error": "Angle out of range"}), 400
    
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
    
    converted_l = frontend_to_backend_coords(l) if l else None
    # Apply horizontal flipping for right metadata
    converted_r = frontend_to_backend_coords(r, flip_horizontal=False) if r else None
    
    controller.update_landmarks(converted_l, converted_r, stage)
    
    return jsonify({"message": "update landmarks"})

@app.route('/next', methods=['POST'])
def next():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    controller.uistates = 'next'
    return jsonify({"message": "uistate next"})

@app.route('/edit', methods=['POST'])
def edit():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    state = request.json.get('uistates')
    controller.uistates = state
    return jsonify({"message": "uistate edit"})

@app.route('/restart', methods=['POST'])
def restart():
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    controller.uistates = 'restart'
    controller.model.resetdata()
    return jsonify({"message": "uistate next"})

@app.route('/screenshot/<int:stage>', methods=['POST'])
def save_screen(stage):
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Create directory if it doesn't exist
    save_dir = f'exam/viewpairs'
    os.makedirs(save_dir, exist_ok=True)
    
    # Save the file
    filename = f'screenshot{stage}.png'
    file_path = os.path.join(save_dir, filename)
    file.save(file_path)
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    image = Image.open(file)
    image_array = np.array(image)
    controller.model.viewpairs[stage] = image_array
    print(controller.model.viewpairs[stage])
    
    return jsonify({"message": f"screenshot saved successfully"})

@app.route('/stitch/<int:stage>')
def get_stitch(stage):
    global controller
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 404
    
    if stage == 0:
        return jsonify({
        'img': None,
        })
    if stage == 1:
        stitch = controller.model.data['pelvis']['stitch']
    if stage == 2:
        stitch = controller.model.data['regcup']['stitch']
    if stage == 3:
        stitch = controller.model.data['regtri']['stitch']
    
    
    # Convert the image to base64 encoding
    _, buffer = cv2.imencode('.jpg', stitch)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Return both image and metadata in JSON
    return jsonify({
        'img': f'data:image/jpeg;base64,{image_base64}',
    })

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
