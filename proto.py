from flask import Flask, jsonify, request, Response, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import io
from PIL import Image
import time
from controller_copy import Controller
from config_manager import ConfigManager
from exam import Exam
from panel import Panel
from flask_cors import CORS
import numpy as np
import json
import base64

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

config = ConfigManager()
with open('config/landmark_config.json', 'r') as f:
    scaf = json.load(f)
with open('config/workflow_config.json', 'r') as f:
    workflow = json.load(f)

class Filter(logging.Filter):
    def filter(self, record):  
        return "api/states" not in record.getMessage()

logger = None
# Configure logging
def setup_logging():
    global logger
    global config

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up the logger
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)  # Set the logging level
    logger.addFilter(Filter())
    
    # Create a file handler
    path_with_vars = config.get("log_config").get("backend_log_path")
    #expanded_path = os.path.expandvars(path_with_vars)
    file_handler = RotatingFileHandler(f'{Path.home()}/AppData/Local/confir/logs/{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))}.log', maxBytes=10000000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    
setup_logging()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


carm_data = None
cpfolder = None

panel = Panel(config, logger) if config.get('testpanel_config').get('panel_on') else None

carm_folder = config.get("carm_folder", "./Calibration")
select = {}
controller = Controller(config, select, panel, logger, cpfolder, scaf, workflow, socketio)



@app.route('/api/image-with-metadata')
def get_image_with_metadata():
    global controller
    global logger

    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        
        image_data = controller.get_image_with_metadata()
        
        # Return both image and converted metadata in JSON
        return jsonify(image_data)
    except Exception as e:
        logger.error(f"Update UI error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/landmarks', methods=['POST'])
def save_landmarks():
    global controller
    global logger

    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        
        stage = request.json.get('stage')
        l = request.json.get('leftMetadata')
        r = request.json.get('rightMetadata')
        limgside = request.json.get('limgside')
        rimgside = request.json.get('rimgside')
        brightness = request.json.get('brightness')
        contrast = request.json.get('contrast')
        
        controller.update_landmarks(l, r, limgside, rimgside, brightness, contrast, stage)
        
        return jsonify({"message": "update landmarks"})
    except Exception as e:
        logger.error(f"Update landmarks error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/next', methods=['POST'])
def next():
    global controller
    global logger
    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        state = request.json.get('uistates')
        stage = request.json.get('stage')
        controller.next(state, stage)

        return jsonify({"message": "uistates updated"})
    except Exception as e:
        logger.error(f"Moving next error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/screenshot/<int:stage>', methods=['POST'])
def save_screen(stage):
    global controller
    global logger
    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404

        if 'image' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        controller.save_screen(stage, file)
        
        return jsonify({"message": f"screenshot saved successfully"})
    except Exception as e:
        logger.error(f"Save screenshot error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/screenshot/<int:stage>')
def get_screen(stage):
    global controller
    global logger
    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        
        return jsonify(controller.get_screen(stage))
    except Exception as e:
        logger.error(f"Load screenshot error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/stitch/<int:stage>')
def get_stitch(stage):
    global controller
    global logger
    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404
        
        return jsonify(controller.get_stitch(stage))
    except Exception as e:
        logger.error(f"Load stitch error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/patient', methods=['POST'])
def patient():
    global controller
    global logger
    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404

        controller.patient(request.get_json())

        return jsonify({"message": f"patient saved successfully"})
    except Exception as e:
        logger.error(f"Save patient error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/pdf')
def pdf():
    global controller
    global logger
    try:
        if controller is None:
            return jsonify({"error": "Controller not initialized"}), 404

        controller.savepdf()

        return jsonify({"message": f"pdf saved successfully"})
    except Exception as e:
        logger.error(f"Save report error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    global carm_data
    global controller

    carm_data, combobox = Exam.get_carms(carm_folder)
    controller.viewmodel.update_setup({'carm_model': combobox})


@socketio.on('carm')
def send_carmimg(id, filename):
    global controller
    global select
    global carm_data
    global cpfolder

    try:
        filename = filename.split('/')[-1]

        select, cpfolder = Exam.serve_carm_select(carm_folder, filename, carm_data)
        image_base64 = Exam.serve_carm_image(carm_folder, filename)

        controller.viewmodel.update_setup({
            'carm_img': f'data:image/jpeg;base64,{image_base64}',
            'selectedCArm': id
        })
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")

@socketio.on('video')
def check_video():
    global controller
    global select
    global cpfolder
    
    controller.update_select(select, cpfolder)      
    controller.viewmodel.update_setup({'loading': True})
    result = controller.connect_video()
    controller.viewmodel.update_setup({'is_connected': result, 'loading': False})

@socketio.on('step')
def change_step(v):
    controller.viewmodel.update_setup({'currentStep': v})

@socketio.on('disconnect')
def handle_disconnect():
    print("666666666666666666666666666666666666 Client disconnected")

if __name__ == '__main__':
    socketio.run(app, host="localhost")
