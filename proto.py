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
import os

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

def encode_image_to_jpeg(image):
    """Convert OpenCV image to JPEG bytes"""
    if image is None:
        return None
    _, encoded_image = cv2.imencode('.jpg', image)
    return encoded_image.tobytes()

@app.route('/devices', methods=['GET'])
def get_devices():
    """Get available calibrated devices"""
    try:
        global controller
        if controller is None:
            controller = ImageProcessingController(FrameGrabber(), AnalyzeBox())
        devices = controller.get_devices()
        return jsonify({"devices": devices})
    except Exception as e:
        app.logger.debug(e)
        return jsonify({"error": str(e)}), 500

@app.route('/mock', methods=['POST'])
def mock():
    global controller
    
    with server_lock:
        if controller is None:
            controller = ImageProcessingController(FrameGrabber(), AnalyzeBox())

        if controller.model.mode == 1:
            controller.model.mode = 0
            controller.run_simulation()
            controller.start_processing()
        else:
            controller.model.mode = 0
            controller.stop_simulation()
        return jsonify({"message": f"Started simulation"})


@app.route('/run', methods=['POST'])
def start_processing():
    """Start video capture and frame processing"""
    global controller
    
    with server_lock:
        if controller is None:
            controller = ImageProcessingController(FrameGrabber(), AnalyzeBox())
        
        if controller.is_running:
            return jsonify({"error": "Processing is already running"}), 400
        
        device_name = request.json.get('device_name')
        if not device_name:
            return jsonify({"error": "Device name is required"}), 400
        
        # Connect to the video device and start processing
        result = controller.start(device_name)
        if isinstance(result, str):
            return jsonify({"error": result}), 500
        
        return jsonify({"message": f"Started processing on device: {device_name}"})

@app.route('/end', methods=['POST'])
def stop_processing():
    """Stop video capture and frame processing"""
    global controller
    
    with server_lock:
        if controller is None or not controller.is_running:
            return jsonify({"error": "Processing is not running"}), 400
        
        controller.stop()
        return jsonify({"message": "Processing stopped successfully"})

@app.route('/attempt/<int:index>/stage/<int:stage>/frame/<frame>', methods=['GET'])
def get_attempt_image(index, stage, frame):
    """Get a specific image from an attempt, stage, and frame"""
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 404

    attempt = controller.viewmodel.get_attempt(index)
    if not attempt:
        return jsonify({"error": f"No attempt available at index {index}"}), 404

    try:
        stage_idx = stage - 1
        
        # Handle special case for stitched image
        if frame == 'stitch':
            image = attempt.stages[stage_idx].stitched
        else:
            image = attempt.stages[stage_idx].frames[int(frame)-1].image

        if image is None:
            return jsonify({"error": f"No image available for stage {stage}, frame {frame}"}), 404
        
        image_bytes = encode_image_to_jpeg(image)
        return Response(image_bytes, mimetype='image/jpeg')
    except (IndexError, AttributeError) as e:
        return jsonify({"error": f"Error accessing image: {str(e)}"}), 404

@app.route('/attempts', methods=['GET'])
def get_attempts():
    """Get information about all processing attempts"""
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 400
    
    def get_stage_status(stage):
        frames_status = [frame is not None for frame in stage.frames]
        return {
            "frames_complete": frames_status,
            "has_stitched": stage.stitched is not None
        }
    
    attempts_info = [
        {
            "index": i,
            "timestamp": attempt.timestamp,
            "stages": [get_stage_status(stage) for stage in attempt.stages]
        }
        for i, attempt in enumerate(controller.viewmodel.attempts)
    ]
    return jsonify({"attempts": attempts_info})

@app.route('/reset_all', methods=['POST'])
def reset_all_attempts():
    """Reset all processing attempts"""
    global controller
    
    with server_lock:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 400
        
        controller.viewmodel.clear()
        return jsonify({"message": "All attempts have been reset"})

@app.route('/retake', methods=['POST'])
def retake():
    """Reset all processing attempts"""
    global controller
    
    with server_lock:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 400
        
        controller.retake()
        return jsonify({"message": "Back to last frame to retake"})


@app.route('/progress', methods=['GET'])
def get_progress():
    """Get current processing progress"""
    global controller, analyze_box
    
    if controller is None:
        return jsonify({"error": "Controller not initialized"}), 400
    
    state = controller.get_current_state()
    return jsonify(state)

@app.route('/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    global controller, frame_grabber
    
    status = {
        "frame_grabber_connected": frame_grabber is not None and frame_grabber.is_connected,
        "processing_running": controller is not None and controller.is_running,
        "device_name": frame_grabber.device_name if frame_grabber else None
    }
    return jsonify(status)

@app.route('/redo', methods=['POST'])
def redo_processing():
    """Reset images and restart processing"""
    global controller
    
    with server_lock:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 400
        
        # Reset images
        controller.first_cropped_image = None
        controller.second_cropped_image = None
        controller.stitched_result = None
        controller.is_stitching = False
        
        return jsonify({"message": "Processing restarted"})

@app.route('/new_processing', methods=['POST'])
def new_processing():
    """Reset images and prepare for new processing attempt"""
    global controller
    
    with server_lock:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 400
        
        # Start a new attempt
        controller.viewmodel.new_attempt()
        print(controller.viewmodel.current_attempt)
        
        return jsonify({"message": "New processing attempt initialized"})

import json
METADATA_FILE = 'metadata.json'

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

@app.route('/metadata/<int:attempt>/<int:stage>/<int:frame>', methods=['GET'])
def get_frame_metadata(attempt, stage, frame):
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 404

    metadata = controller.viewmodel.get_frame_metadata(attempt, stage, frame)
    response = jsonify(metadata)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/metadata/<int:attempt>/<int:stage>/<int:frame>', methods=['POST'])
def update_frame_metadata(attempt, stage, frame):
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 404

    try:
        updated_metadata = request.json
        save_metadata(updated_metadata)
        controller.viewmodel.attempts[attempt].stages[stage-1].frames[frame-1].metadata = updated_metadata
        response = jsonify({"message": "Metadata updated successfully"})
    except Exception as e:
        response = jsonify({"error": str(e)}), 400
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
@app.route('/next_frame', methods=['POST'])
def next_frame():
    """Trigger processing of next frame in simulation mode"""
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 404
        
    if controller.model.mode != 0:  # Check if in simulation mode
        return jsonify({"error": "Not in simulation mode"}), 400
        
    controller.process_next_frame = True  # New flag to control frame progression
    return jsonify({"message": "Processing next frame"})

from flask import send_file
from io import BytesIO

@app.route('/adjust_brightness/<int:index>/<int:stage>/<int:frame>', methods=['POST'])
def adjust_brightness(index, stage, frame):
    """Adjust brightness of a specific image from an attempt, stage, and frame"""
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 404

    attempt = controller.viewmodel.get_attempt(index)
    if not attempt:
        return jsonify({"error": f"No attempt available at index {index}"}), 404

    data = request.json
    brightness = data.get('brightness', 0)

    try:
        stage_idx = stage - 1
        frame_idx = int(frame) - 1
        
        # Get the original image
        original_image = controller.model.images[stage_idx][frame_idx]

        
        image_bytes = encode_image_to_jpeg(original_image)
        return Response(image_bytes, mimetype='image/jpeg')
    except (IndexError, AttributeError) as e:
        return jsonify({"error": f"Error accessing or adjusting image: {str(e)}"}), 404

@app.route('/save_overlay_image/<int:attempt_index>/<int:sub_attempt>/<int:frame_number>', methods=['POST'])
def save_image(attempt_index, sub_attempt, frame_number):
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Create directory if it doesn't exist
    save_dir = f'data/attempts/{attempt_index}/sub_attempts/{sub_attempt}'
    os.makedirs(save_dir, exist_ok=True)
    
    # Save the file
    filename = f'composite_frame_{frame_number}.png'
    file_path = os.path.join(save_dir, filename)
    file.save(file_path)
    
    return jsonify({"message": f"Composite image for frame {frame_number} saved successfully"})


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
    
    # Return both image and metadata in JSON
    return jsonify({
        'image': f'data:image/jpeg;base64,{image_base64}',
        'metadata': image_data['metadata'],
        'checkmark': image_data['checkmark'],
        'error': image_data['error']
    })
@app.route('/landmarks', methods=['POST'])
def landmarks():
    l = request.json.get('leftMetadata')
    r = request.json.get('rightMetadata')
    print(l,r)
    return jsonify({"done"})

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
