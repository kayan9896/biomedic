from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)
last=None
def frame_difference(frame1, frame2):
    if frame1 is None or frame2 is None:
        return True
    
    diff = cv2.absdiff(frame1, frame2)
    return np.mean(diff) > 10 

def generate_frames():
    global last
    camera = cv2.VideoCapture(0)  # Use 0 for default camera

    while True:
        success, frame = camera.read()
        if not success:
            break
        if not frame_difference(last,frame):
            continue
        else:
            last=frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/time')
def get_server_time():
    current_time = datetime.now()
    print(current_time)
    return jsonify({'time': str(current_time)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)