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
    
    attempts_info = []
    for i, attempt in enumerate(controller.viewmodel.attempts):
        stage_info = []
        for stage_idx, stage in enumerate(attempt.stages):
            sub_attempts_info = []
            for sub_idx, sub in enumerate(stage.sub_attempts):
                sub_attempts_info.append({
                    "has_image1": sub.image1 is not None,
                    "has_image2": sub.image2 is not None,
                    "has_stitch": sub.stitch is not None
                })
            stage_info.append({"sub_attempts": sub_attempts_info})
        
        attempts_info.append({
            "index": i,
            "timestamp": attempt.timestamp,
            "stages": stage_info
        })
    
    return jsonify({"attempts": attempts_info})

@app.route('/attempt/<int:index>/stage/<int:stage>/frame/<int:frame>', methods=['GET'])
def get_attempt_frame(index, stage, frame):
    """Get a specific frame from a stage"""
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 400
    
    attempt = controller.viewmodel.get_attempt(index)
    if not attempt or stage < 0 or stage >= len(attempt.stages):
        return jsonify({"error": "Invalid attempt or stage"}), 404
    
    stage_obj = attempt.stages[stage]
    sub_attempt_idx = (frame - 1) // 2
    frame_in_sub = (frame - 1) % 2 + 1
    
    if sub_attempt_idx >= len(stage_obj.sub_attempts):
        return jsonify({"error": "Invalid frame number"}), 404
    
    image = None
    if frame_in_sub == 1:
        image = stage_obj.sub_attempts[sub_attempt_idx].image1
    else:
        image = stage_obj.sub_attempts[sub_attempt_idx].image2
    
    if image is None:
        return jsonify({"error": "Image not available"}), 404
    
    image_bytes = encode_image_to_jpeg(image)
    return Response(image_bytes, mimetype='image/jpeg')

@app.route('/attempt/<int:index>/stage/<int:stage>/sub_attempt/<int:sub>/stitch', methods=['GET'])
def get_stitch_result(index, stage, sub):
    """Get the stitched result for a specific sub-attempt"""
    global controller
    if not controller:
        return jsonify({"error": "Controller not initialized"}), 400
    
    attempt = controller.viewmodel.get_attempt(index)
    if not attempt or stage < 0 or stage >= len(attempt.stages):
        return jsonify({"error": "Invalid attempt or stage"}), 404
    
    stage_obj = attempt.stages[stage]
    if sub >= len(stage_obj.sub_attempts):
        return jsonify({"error": "Invalid sub-attempt"}), 404
    
    stitch = stage_obj.sub_attempts[sub].stitch
    if stitch is None:
        return jsonify({"error": "Stitch result not available"}), 404
    
    image_bytes = encode_image_to_jpeg(stitch)
    return Response(image_bytes, mimetype='image/jpeg')

@app.route('/reset_all', methods=['POST'])
def reset_all():
    """Reset all attempts and start fresh"""
    global controller
    
    with server_lock:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 400
        
        controller.viewmodel.clear()
        controller.viewmodel.new_attempt()
        
        return jsonify({"message": "All attempts reset successfully"})
        
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


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)