import os
import time
import json
import logging
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import RotatingFileHandler
import pandas as pd

csvf = {}
test_result = False

test_case = {}
for page in os.listdir('ui_testdata'):
    test_case[page] = {}
    for group in os.listdir(f'ui_testdata/{page}'):
        test_case[page][group] = {}
        for case in os.listdir(f'ui_testdata/{page}/{group}'):
            test_case[page][group][case[:-5]] = {}
current_case = {}
# Logging filter
class Filter(logging.Filter):
    def filter(self, record):
        return "404" not in record.getMessage()

# Configure logging
logger = None
def setup_logging():
    global logger
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('uvicorn.access')
    logger.setLevel(logging.DEBUG)
    logger.addFilter(Filter())

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

# Endpoints


@app.get("/carm-images/{filename}")
def serve_carm_image(filename: str):
    global test_result
    global current_case
    test_result = current_case['api_data'] == filename and current_case['route'] == f'/carm-images/{filename}'
    print(f'API called: /carm-images/{filename}')
    print(f'Selected carm:{filename}')
    return {
        "image": f"data:image/jpeg;base64,{0}",
        "imu_on": True
    }


@app.get("/check-video-connection")
def check_video_connection():
    global test_result
    global current_case
    test_result = current_case['route'] == f'/check-video-connection'
    print(f'API called: /check-video-connection')
    return {"connected": True}
    
@app.get("/check-tilt-sensor")
def check_tilt_sensor():
    print(f'API called: /check-tilt-sensor')
    return {"connected": True}

@app.post("/run2")
def start_processing():
    print(f'API called: /run2')
    return {"connected": True}

@app.post("/label")
async def switch_side(request: Request):
    dt = await request.json()
    print(f'Sent data: {dt}')
    print(f'API called: /label')
    return {"connected": True}

@app.post("/next")
async def next(request: Request):
    dt = await request.json()
    print(f'Sent data: {dt}')
    print(f'API called: /next')
    return {"connected": True}

@app.get("/result")
def csv():
    global test_result
    return {"result": test_result} 

@app.post("/csv")
async def csv(request: Request):
    global csvf
    dt = await request.json()
    
    pd.DataFrame.from_dict(data = dt, orient='index').to_csv('uitest.csv', header=False)
    return {"connected": True}

@app.get("/cases")
async def cases(request: Request):
    global test_case
    return test_case

@app.get("/casedata/{page}/{group}/{case}")
async def cases(page, group, case):
    global current_case
    with open(f'ui_testdata/{page}/{group}/{case}.json', 'r') as f:
        current_case = json.load(f)

    return current_case
