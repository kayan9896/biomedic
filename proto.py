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
    global frame_grabber
    if frame_grabber is None:
        frame_grabber = FrameGrabber()
    devices = frame_grabber.get_available_devices()
    return jsonify({"devices": list(devices.keys())})

@app.route('/run', methods=['POST'])
def start_processing():
    """Start video capture and frame processing"""
    global frame_grabber, analyze_box, controller
    
    with server_lock:
        if controller and controller.is_running:
            return jsonify({"error": "Processing is already running"}), 400
        
        device_name = request.json.get('device_name')
        if not device_name:
            return jsonify({"error": "Device name is required"}), 400
        
        # Initialize components if not already initialized
        if frame_grabber is None:
            frame_grabber = FrameGrabber()
        if analyze_box is None:
            analyze_box = AnalyzeBox()
        if controller is None:
            controller = ImageProcessingController(frame_grabber, analyze_box)
        
        # Connect to the video device
        result = frame_grabber.initiateVideo(device_name)
        if isinstance(result, str):
            return jsonify({"error": result}), 500
        
        # Start video capture and processing
        frame_grabber.startVideo()
        controller.start_processing()
        
        return jsonify({"message": f"Started processing on device: {device_name}"})

@app.route('/end', methods=['POST'])
def stop_processing():
    """Stop video capture and frame processing"""
    global controller, frame_grabber
    
    with server_lock:
        if controller is None or not controller.is_running:
            return jsonify({"error": "Processing is not running"}), 400
        
        controller.stop_processing()
        frame_grabber.stopVideo()
        frame_grabber.closeVideo()
        
        return jsonify({"message": "Processing stopped successfully"})

@app.route('/image1', methods=['GET'])
def get_first_image():
    """Serve the first cropped image"""
    global controller
    if controller is None or controller.first_cropped_image is None:
        return jsonify({"error": "No first image available"}), 404
    
    image_bytes = encode_image_to_jpeg(controller.first_cropped_image)
    return Response(image_bytes, mimetype='image/jpeg')

@app.route('/image2', methods=['GET'])
def get_second_image():
    """Serve the second cropped image"""
    global controller
    if controller is None or controller.second_cropped_image is None:
        return jsonify({"error": "No second image available"}), 404
    
    image_bytes = encode_image_to_jpeg(controller.second_cropped_image)
    return Response(image_bytes, mimetype='image/jpeg')

@app.route('/stitch', methods=['GET'])
def get_stitched_image():
    """Serve the stitched image"""
    global controller
    if controller is None or controller.stitched_result is None:
        return jsonify({"error": "No stitched image available"}), 404
    
    image_bytes = encode_image_to_jpeg(controller.stitched_result)
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
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)