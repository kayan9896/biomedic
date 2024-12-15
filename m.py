from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
from datetime import datetime
import threading
import time
import base64

app = Flask(__name__)
CORS(app)

camera = cv2.VideoCapture(0)
last_frame = None
current_capture = None
is_capturing = False
capture_complete = threading.Event()

def frame_difference(frame1, frame2):
    if frame1 is None or frame2 is None:
        return True
    diff = cv2.absdiff(frame1, frame2)
    return np.mean(diff) > 10 

def generate_frames():
    global last_frame, current_capture, is_capturing
    while is_capturing:
        success, frame = camera.read()
        if success:
            if frame_difference(last_frame, frame):
                current_capture = frame
                last_frame = frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        #time.sleep(0.1)

@app.route('/video_stream')
def video_stream():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_capture', methods=['POST'])
def start_capture():
    global is_capturing, current_capture
    is_capturing = True
    current_capture = None
    capture_complete.clear()
    return jsonify({"status": "Capture started"})

@app.route('/end_capture', methods=['POST'])
def end_capture():
    global is_capturing, current_capture
    is_capturing = False
    capture_complete.set()
    if current_capture is not None:
        _, buffer = cv2.imencode('.jpg', current_capture)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({"status": "Capture ended", "image": image_base64})
    else:
        return jsonify({"status": "No change detected"})
    
@app.route('/time')
def get_server_time():
    current_time = datetime.now()
    print(current_time)
    return jsonify({'time': str(current_time)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)