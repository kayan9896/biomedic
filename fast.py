import os
import time
import threading
import logging
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import RotatingFileHandler

from model import Model
from fg import FrameGrabber
from controller import Controller
from config_manager import ConfigManager
from calibrate import Calibrate
from panel import Panel


# Logging filter
class Filter(logging.Filter):
    def filter(self, record):
        return "api/states" not in record.getMessage()

# Configure logging
logger = None
def setup_logging():
    global logger
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('uvicorn')
    logger.setLevel(logging.DEBUG)
    logger.addFilter(Filter())

    file_handler = RotatingFileHandler(
        f'logs/{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}.log',
        maxBytes=10_000_000,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

setup_logging()

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
frame_grabber = None
analyze_box = None
controller = None

config = ConfigManager()
calibrate = Calibrate()
panel = Panel(config, logger) if config.get('on_simulation') else None
server_lock = threading.Lock()

carm_folder = config.get("carm_folder", "./Calibration")
select = {}

# Endpoints
@app.get("/get-carms")
def get_carms():
    global panel, controller, logger
    if panel and panel.jumpped:
        controller = panel.controller
        return {"jump": True}
    try:
        carm_data = calibrate.get_carms(carm_folder)
        return carm_data
    except Exception as e:
        logger.error(f"Error fetching C-arm data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/carm-images/{filename}")
def serve_carm_image(filename: str):
    global select, controller, logger
    if controller:
        controller = None
    try:
        select = calibrate.serve_carm_select(carm_folder, filename)
        image_base64 = calibrate.serve_carm_image(carm_folder, filename)
        return {
            "image": f"data:image/jpeg;base64,{image_base64}",
            "imu_on": select['IMU']['imu_on']
        }
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/check-video-connection")
def check_video_connection():
    global controller, select, panel, logger
    with server_lock:
        if controller is None:
            controller = Controller(config, select, panel, logger)
        result = controller.connect_video()
        return result
    
@app.get("/check-tilt-sensor")
def check_tilt_sensor():
    global controller
    with server_lock:
        if controller is None:
            controller = Controller(config)
        return controller.imu_sensor.check_tilt_sensor()

@app.post("/run2")
def start_processing():
    global controller, logger
    try:
        with server_lock:
            if controller is None:
                controller = Controller(config)

            result = controller.start_processing()
            if not result:
                raise HTTPException(status_code=400, detail="Processing is already running")

            templates = controller.load()
            return {"message": "Started processing on device", "templates": templates}
    except Exception as e:
        logger.error(f"Fail to start controller loop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/states")
def get_states():
    global controller, logger
    try:
        return controller.get_states()
    except Exception as e:
        logger.error(f"Fail to get states: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/setting")
async def set_ai_autocollect_modes(request: Request):
    global controller, logger
    try:
        if controller is None:
            controller = Controller()
        data = await request.json()
        controller.set_ai_autocollect_modes(data)
        return {"success": True}
    except Exception as e:
        logger.error(f"Setting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/image-with-metadata")
def get_image_with_metadata():
    global controller, logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        image_data = controller.get_image_with_metadata()
        return image_data
    except Exception as e:
        logger.error(f"Update UI error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/landmarks')
async def save_landmarks(request: Request):
    global controller
    global logger

    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        data = await request.json()
        stage = data.get('stage')
        l = data.get('leftMetadata')
        r = data.get('rightMetadata')
        limgside = data.get('limgside')
        rimgside = data.get('rimgside')
        brightness = data.get('brightness')
        contrast = data.get('contrast')
        
        controller.update_landmarks(l, r, limgside, rimgside, brightness, contrast, stage)
        
        return {"message": "update landmarks"}
    except Exception as e:
        logger.error(f"Update landmarks error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/cap')
async def manual_framecap(request: Request):
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        state = await request.json().get('cap')
        controller.do_capture = state
        return {"message": "do capture"}
    except Exception as e:
        logger.error(f"Manual capture error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post('/label')
async def switch_side(request: Request):
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        label = await request.json().get('label')
        controller.active_side = label
        return {"message": "click label switch active side"}
    except Exception as e:
        logger.error(f"Manual switch side error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post('/edit')
async def edit(request: Request):
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        data = await request.json()
        state = data.get('uistates')
        controller.pause_states = state
        return {"message": "pause_states updated"}
    except Exception as e:
        logger.error(f"Edit/pause error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post('/next')
async def next(request: Request):
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        state = await request.json().get('uistates')
        stage = await request.json().get('stage')
        controller.next(state, stage)

        return {"message": "uistates updated"}
    except Exception as e:
        logger.error(f"Moving next error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post('/restart')
def restart():
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        controller.restart()

        return {"message": "uistate restart"}
    except Exception as e:
        logger.error(f"Restart error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post("/screenshot/{stage}")
async def save_screen(stage: int, image: UploadFile = File(...)):
    global controller
    if controller is None:
        raise HTTPException(status_code=404, detail="Controller not initialized")
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No selected file")
        controller.save_screen(stage, image.file)
        return {"message": "screenshot saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/screenshot/{stage}')
def get_screen(stage):
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        
        return controller.get_screen(stage)
    except Exception as e:
        logger.error(f"Load screenshot error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get('/stitch/{stage}')
def get_stitch(stage):
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        
        return controller.get_stitch(stage)
    except Exception as e:
        logger.error(f"Load stitch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/patient')
async def patient(request: Request):
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")
        data = await request.json()
        controller.patient(data)

        return {"message": f"patient saved successfully"}
    except Exception as e:
        logger.error(f"Save patient error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.route('/pdf')
def pdf():
    global controller
    global logger
    try:
        if controller is None:
            raise HTTPException(status_code=404, detail="Controller not initialized")

        controller.savepdf()

        return {"message": f"pdf saved successfully"}
    except Exception as e:
        logger.error(f"Save report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))