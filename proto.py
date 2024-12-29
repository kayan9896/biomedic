from flask import Flask, jsonify, request, Response
import cv2
import threading
import io
from PIL import Image
import time
from ab import AnalyzeBox
from fg import FrameGrabber
from be import ImageProcessingController
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    """Get available video devices"""
    global controller
    if controller is None:
        controller = ImageProcessingController(FrameGrabber(), AnalyzeBox())
    devices = controller.frame_grabber.get_available_devices()
    return jsonify({"devices": list(devices.keys())})

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

@app.route('/attempts', methods=['GET'])
def get_attempts():
    """Get information about all processing attempts"""
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 400
    
    attempts_info = [
        {
            "index": i,
            "timestamp": attempt.timestamp,
            "has_first_image": attempt.first_cropped_image is not None,
            "has_second_image": attempt.second_cropped_image is not None,
            "has_stitched_result": attempt.stitched_result is not None
        }
        for i, attempt in enumerate(controller.model.attempts)
    ]
    return jsonify({"attempts": attempts_info})

@app.route('/attempt/<int:index>/image1', methods=['GET'])
def get_attempt_first_image(index):
    """Get the first image of a specific attempt"""
    global controller
    attempt = controller.model.get_attempt(index) if controller else None
    if not attempt or attempt.first_cropped_image is None:
        return jsonify({"error": f"No first image available for attempt {index}"}), 404
    
    image_bytes = encode_image_to_jpeg(attempt.first_cropped_image)
    return Response(image_bytes, mimetype='image/jpeg')

@app.route('/attempt/<int:index>/image2', methods=['GET'])
def get_attempt_sec_image(index):
    """Get the first image of a specific attempt"""
    global controller
    attempt = controller.model.get_attempt(index) if controller else None
    if not attempt or attempt.second_cropped_image is None:
        return jsonify({"error": f"No 2 image available for attempt {index}"}), 404
    
    image_bytes = encode_image_to_jpeg(attempt.second_cropped_image)
    return Response(image_bytes, mimetype='image/jpeg')
    
@app.route('/attempt/<int:index>/stitch', methods=['GET'])
def get_stitched_image(index):
    """Serve the stitched image"""
    global controller
    attempt = controller.model.get_attempt(index) if controller else None
    if not attempt or attempt.stitched_result is None:
        return jsonify({"error": f"No 2 image available for attempt {index}"}), 404
     
    image_bytes = encode_image_to_jpeg(attempt.stitched_result)
    return Response(image_bytes, mimetype='image/jpeg')

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
        controller.model.new_attempt()
        print(controller.model.current_attempt)
        
        return jsonify({"message": "New processing attempt initialized"})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)