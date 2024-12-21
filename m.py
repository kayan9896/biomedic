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

class Framegrab:
    def __init__(self):
        self.camera = cv2.VideoCapture(1)
        self.last_frame = None
        self.current_capture = None
        self.is_capturing = False
        self.capture_complete = threading.Event()

    def frame_difference(self, frame1, frame2):
        if frame1 is None or frame2 is None:
            return True
        diff = cv2.absdiff(frame1, frame2)
        return np.mean(diff) > 10 

    def generate_frames(self):
        while self.is_capturing:
            success, frame = self.camera.read()
            if success:
                print(success)
                if self.frame_difference(self.last_frame, frame):
                    self.current_capture = frame
                    self.last_frame = frame
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            #time.sleep(0.1)
fg=Framegrab()
@app.route('/video_stream')
def video_stream():
    return Response(fg.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_capture', methods=['POST'])
def start_capture():
    fg.is_capturing = True
    fg.current_capture = None
    fg.capture_complete.clear()
    return jsonify({"status": "Capture started"})

@app.route('/end_capture', methods=['POST'])
def end_capture():
    fg.is_capturing = False
    fg.capture_complete.set()
    if fg.current_capture is not None:
        _, buffer = cv2.imencode('.jpg', fg.current_capture)
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