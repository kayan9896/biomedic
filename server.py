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
first_image_state = ImageState()
second_image_state = ImageState()
current_phase = 1  # 1 for first image, 2 for second image comparison

def validate_image():
    return random.random() < 0.5

def compare_images(img1, img2):
    # Convert images to numpy arrays and compare
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    return np.array_equal(arr1, arr2)

def image_detection_thread():
    global current_phase
    
    while True:
        time.sleep(5)  # Check every 5 seconds
        
        if os.path.exists(image_path):
            current_state = first_image_state if current_phase == 1 else second_image_state
            
            if current_phase == 1:
                is_valid = validate_image()
                
                if is_valid:
                    current_state.has_valid_image = True
                    current_state.error_message = None
                    current_state.is_detecting = False
                    current_state.image = Image.open(image_path)
                else:
                    current_state.has_valid_image = False
                    current_state.error_message = "Image validation failed"
            
            elif current_phase == 2 and first_image_state.has_valid_image:
                new_image = Image.open(image_path)
                are_different = not compare_images(first_image_state.image, new_image)
                
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
    state = first_image_state if phase == 1 else second_image_state
    return jsonify({
        'is_detecting': state.is_detecting,
        'error_message': state.error_message,
        'has_valid_image': state.has_valid_image
    })

@app.route('/image/<int:phase>')
def get_image(phase):
    state = first_image_state if phase == 1 else second_image_state
    if state.has_valid_image:
        return send_file(image_path, mimetype='image/png')
    else:
        return jsonify({'error': 'No valid image available'}), 404

@app.route('/start-phase-two')
def start_phase_two():
    global current_phase
    current_phase = 2
    second_image_state.is_detecting = True
    second_image_state.has_valid_image = False
    second_image_state.error_message = None
    return jsonify({'status': 'Phase two started'})

if __name__ == '__main__':
    app.run(debug=True)