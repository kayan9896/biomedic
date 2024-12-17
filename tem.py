from flask import Flask, send_file, jsonify, request
import numpy as np
from PIL import Image
from flask_cors import CORS
import io
import random

app = Flask(__name__)
CORS(app)

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
        #self.points = generate_random_points(self.image)

@app.route('/image')
def get_cup_raw_image():
    state = CupImageState()
    state.load_random_image()
    if state.image:
        img_io = io.BytesIO()
        state.image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No image available'}), 404

if __name__ == '__main__':
    app.run(debug=True)