from flask import Flask, send_file, jsonify, request
import threading
import time
import random
import cv2
import numpy as np
from PIL import Image
import io
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

class ImageState:
    def __init__(self):
        self.is_detecting = True
        self.error_message = None
        self.has_valid_image = False
        self.image = None
        self.points = []
        self.last_frame = None  # Store last frame for comparison

# Global variables
image_states = {
    1: ImageState(),
    2: ImageState(),
    3: ImageState(),
    4: ImageState()
}
current_phase = 1
comparison_pairs = {2: 1, 4: 3}
is_detection_active = False
p=None


def reset_states():
    global current_phase
    current_phase = 1
    for state in image_states.values():
        state.is_detecting = True
        state.error_message = None
        state.has_valid_image = False
        state.image = None
        state.last_frame = None

def validate_image(f):
    return random.random() < 0.7


def frame_difference(frame1, frame2):
    if frame1 is None or frame2 is None:
        return True
    
    diff = cv2.absdiff(frame1, frame2)
    return np.mean(diff) > 10 

def image_detection_thread():
    global current_phase, is_detection_active, p
    
    cap = cv2.VideoCapture(0) 
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    while True:
        if not is_detection_active:
            time.sleep(1)  # Sleep when detection is not active
            continue

        ret, frame = cap.read()
        if not ret:
            continue
        if not frame_difference(frame, p):
            continue
        p=frame
        current_state = image_states[current_phase]
        if current_state.is_detecting == False: continue
        if current_phase in [1, 3]:  # First image of each pair
            
            current_state.last_frame = frame.copy()
            
            if validate_image(frame):
                # Convert CV2 frame to PIL Image
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                current_state.has_valid_image = True
                current_state.error_message = None
                current_state.is_detecting = False
                current_state.image = pil_image
                print(frame,current_phase,current_state.is_detecting,current_state.has_valid_image)
            else:
                current_state.has_valid_image = False
                current_state.error_message = "Image validation failed"
                    
                
        elif current_phase in [2, 4]:  # Second image of each pair
            compare_with = comparison_pairs[current_phase]
            if image_states[compare_with].has_valid_image:
                
                current_state.last_frame = frame.copy()
                
                # Convert current frame to RGB for comparison
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                current_array = np.array(rgb_frame)
                previous_array = np.array(image_states[compare_with].image)
                
                if not np.array_equal(current_array, previous_array):
                    pil_image = Image.fromarray(rgb_frame)
                    current_state.has_valid_image = True
                    current_state.error_message = None
                    current_state.is_detecting = False
                    current_state.image = pil_image
                else:
                    current_state.has_valid_image = False
                    current_state.error_message = "Images are too similar"

        #time.sleep(3)  # Small delay to prevent excessive CPU usage

    cap.release()

# Start the detection thread
detection_thread = threading.Thread(target=image_detection_thread)
detection_thread.daemon = True
detection_thread.start()

# Modified get_raw_image to serve camera frame
@app.route('/raw-image/<int:phase>')
def get_raw_image(phase):
    state = image_states[phase]
    if state.has_valid_image and state.image:
        img_io = io.BytesIO()
        state.image.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No valid image available'}), 404

@app.route('/start-detection')
def start_detection():
    global is_detection_active
    is_detection_active = True
    return jsonify({'status': 'Detection started'})

@app.route('/stop-detection')
def stop_detection():
    global is_detection_active
    is_detection_active = False
    return jsonify({'status': 'Detection stopped'})

@app.route('/status/<int:phase>')
def get_status(phase):
    state = image_states[phase]
    return jsonify({
        'is_detecting': state.is_detecting,
        'error_message': state.error_message,
        'has_valid_image': state.has_valid_image
    })

def generate_random_points(image):
    width, height = image.size
    num_points = random.randint(3, 6)  # Random number of points between 3 and 6
    points = []
    for _ in range(num_points):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        points.append({"x": x, "y": y})
    return points

@app.route('/image/<int:phase>')
def get_image(phase):
    state = image_states[phase]
    if state.has_valid_image:
        if not state.points:
            state.points = generate_random_points(state.image)
        
        width, height = state.image.size
        return jsonify({
            'imageUrl': f'/raw-image/{phase}',
            'points': state.points,
            'width': width,
            'height': height
        })
    else:
        return jsonify({'error': 'No valid image available'}), 404

@app.route('/update-points/<int:phase>', methods=['POST'])
def update_points(phase):
    data = request.json
    new_points = data.get('points', [])
    image_states[phase].points = new_points
    return jsonify({'status': 'Points updated successfully'})

@app.route('/start-phase/<int:phase>')
def start_phase(phase):
    global current_phase
    current_phase = phase
    image_states[phase].is_detecting = True
    image_states[phase].has_valid_image = False
    image_states[phase].error_message = None
    return jsonify({'status': f'Phase {phase} started'})

@app.route('/reset')
def reset():
    global is_detection_active
    is_detection_active = False
    reset_states()
    return jsonify({'status': 'All states reset'})


IMAGE_PATHS = ['1.png', '2.png', '3.png', '4.png']

# Add this to your global state if needed
cup_image_states = {}

class CupImageState:
    def __init__(self):
        self.image = None
        self.points = None
        self.image_path = None

    def load_random_image(self):
        self.image_path = random.choice(IMAGE_PATHS)
        self.image = Image.open(self.image_path)
        self.points = generate_random_points(self.image)

def get_or_create_cup_state(pair_id, image_index):
    state_key = f"{pair_id}_{image_index}"
    if state_key not in cup_image_states:
        cup_image_states[state_key] = CupImageState()
    return cup_image_states[state_key]

@app.route('/cup/image/<int:pair_id>/<int:image_index>')
def get_cup_image(pair_id, image_index):
    state = get_or_create_cup_state(pair_id, image_index)
    
    if not state.image:
        state.load_random_image()
    
    width, height = state.image.size
    return jsonify({
        'imageUrl': f'/cup/raw-image/{pair_id}/{image_index}',
        'points': state.points,
        'width': width,
        'height': height,
        'imagePath': state.image_path
    })

@app.route('/cup/raw-image/<int:pair_id>/<int:image_index>')
def get_cup_raw_image(pair_id, image_index):
    state = get_or_create_cup_state(pair_id, image_index)
    
    if state.image:
        img_io = io.BytesIO()
        state.image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No image available'}), 404

# Optional: Add a route to reset or clear cup states if needed
@app.route('/cup/reset', methods=['POST'])
def reset_cup_states():
    cup_image_states.clear()
    return jsonify({'message': 'Cup states reset successfully'})

@app.route('/time')
def get_server_time():
    current_time = datetime.now()
    print(current_time)
    return jsonify({'time': str(current_time)})

if __name__ == '__main__':
    app.run(debug=True)