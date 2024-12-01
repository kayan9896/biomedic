from flask import Flask, send_file, jsonify,request
import threading
import time
import random
import os
from flask_cors import CORS
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app)

class ImageState:
    def __init__(self):
        self.is_detecting = True
        self.error_message = None
        self.has_valid_image = False
        self.image = None
        self.points = []

# Global variables
image_path = '2.png'
image_states = {
    1: ImageState(),  # First image
    2: ImageState(),  # Second image
    3: ImageState(),  # Third image
    4: ImageState()   # Fourth image
}
current_phase = 1  # 1-4 for each image
comparison_pairs = {2: 1, 4: 3}  # which images to compare

def reset_states():
    global current_phase
    current_phase = 1
    for state in image_states.values():
        state.is_detecting = True
        state.error_message = None
        state.has_valid_image = False
        state.image = None

def validate_image():
    return random.random() < 0.5

def compare_images(img1, img2):
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    return np.array_equal(arr1, arr2)

def image_detection_thread():
    global current_phase
    
    while True:
        time.sleep(5)  # Check every 5 seconds
        
        if os.path.exists(image_path):
            current_state = image_states[current_phase]
            
            if current_phase in [1, 3]:  # First image of each pair
                is_valid = validate_image()
                
                if is_valid:
                    current_state.has_valid_image = True
                    current_state.error_message = None
                    current_state.is_detecting = False
                    current_state.image = Image.open(image_path)
                else:
                    current_state.has_valid_image = False
                    current_state.error_message = "Image validation failed"
            
            elif current_phase in [2, 4]:  # Second image of each pair
                compare_with = comparison_pairs[current_phase]
                if image_states[compare_with].has_valid_image:
                    new_image = Image.open(image_path)
                    are_different = not compare_images(image_states[compare_with].image, new_image)
                    
                    if are_different:
                        current_state.has_valid_image = True
                        current_state.error_message = None
                        current_state.is_detecting = False
                        current_state.image = new_image
                    else:
                        current_state.has_valid_image = False
                        current_state.error_message = "Images are too similar"

# Start the detection thread
detection_thread = threading.Thread(target=image_detection_thread)
detection_thread.daemon = True
detection_thread.start()

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
        # If points haven't been generated yet, generate them
        if not state.points:
            state.points = generate_random_points(state.image)
        
        return jsonify({
            'imageUrl': f'/raw-image/{phase}',
            'points': state.points
        })
    else:
        return jsonify({'error': 'No valid image available'}), 404

@app.route('/raw-image/<int:phase>')
def get_raw_image(phase):
    state = image_states[phase]
    if state.has_valid_image:
        return send_file(image_path, mimetype='image/png')
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
    reset_states()
    return jsonify({'status': 'All states reset'})

if __name__ == '__main__':
    app.run(debug=True)