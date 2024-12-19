from flask import Flask, send_file, jsonify, request, Response
import numpy as np
from PIL import Image
from flask_cors import CORS
import io
import random
import json
import threading
from libra import compute, progress_tracker  # Import the progress tracker

app = Flask(__name__)
CORS(app)

IMAGE_PATHS = ['1.png', '2.png', '3.png', '4.png']

class CupImageState:
    def __init__(self):
        self.image = None
        self.points = None
        self.image_path = None

    def load_random_image(self):
        self.image_path = random.choice(IMAGE_PATHS)
        self.image = Image.open(self.image_path)

@app.route('/image')
def get_cup_raw_image():
    # Reset progress tracker
    progress_tracker.update(0)

    # Start computation in a separate thread
    thread = threading.Thread(target=compute)
    thread.start()

    # Wait for computation to complete
    thread.join()

    state = CupImageState()
    state.load_random_image()

    if state.image:
        img_io = io.BytesIO()
        state.image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No image available'}), 404

@app.route('/progress')
def progress():
    def generate():
        last_progress = -1
        while True:
            current_progress = progress_tracker.get()
            if current_progress != last_progress:
                yield f"data: {json.dumps({'progress': current_progress})}\n\n"
                last_progress = current_progress

            if current_progress == 100:
                break

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)