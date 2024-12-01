from flask import Flask, send_file, jsonify
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

# Global variables
image_path = '2.png'
image_states = {
    1: ImageState(),  # First image
    2: ImageState(),  # Second image
    3: ImageState(),  # Third image
    4: ImageState()   # Fourth image
}
current_phase = 1  # 1-4 for each image phase
comparison_pairs = {2: 1, 4: 3}  # Which images to compare: 2 compares with 1, 4 compares with 3

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
                comparison_phase = comparison_pairs[current_phase]
                if image_states[comparison_phase].has_valid_image:
                    new_image = Image.open(image_path)
                    are_different = not compare_images(image_states[comparison_phase].image, new_image)
                    
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

@app.route('/image/<int:phase>')
def get_image(phase):
    state = image_states[phase]
    if state.has_valid_image:
        return send_file(image_path, mimetype='image/png')
    else:
        return jsonify({'error': 'No valid image available'}), 404

@app.route('/start-phase/<int:phase>')
def start_phase(phase):
    global current_phase
    if 1 <= phase <= 4:
        current_phase = phase
        image_states[phase].is_detecting = True
        image_states[phase].has_valid_image = False
        image_states[phase].error_message = None
    return jsonify({'status': f'Phase {phase} started'})

@app.route('/reset')
def reset():
    reset_states()
    return jsonify({'status': 'All phases reset'})

if __name__ == '__main__':
    app.run(debug=True)