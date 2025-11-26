import os
import time
import json
import logging
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import RotatingFileHandler
import pandas as pd

csvf = {}
page = None
group = None
test_result = False

test_case = {}
for p in os.listdir('ui_testdata'):
    test_case[p] = {}
    for g in os.listdir(f'ui_testdata/{p}'):
        test_case[p][g] = {}
        for c in os.listdir(f'ui_testdata/{p}/{g}'):
            test_case[p][g][c[:-5]] = {}
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

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                print(message)
            except Exception as e:
                print('off', e, connection)

manager = ConnectionManager()

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
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

@app.get("/carm-images/{filename}")
async def serve_carm_image(filename: str):
    global test_result
    global current_case
    if current_case.get('name', '') == "step:1,carm:null":
        test_result = current_case['api_data'] == filename and current_case['route'] == f'/carm-images/{filename}'
        print(f'API called: /carm-images/{filename}')
        print(f'Selected carm:{filename}')
        await manager.broadcast(json.dumps({"result": test_result}))
    return {
        "image": f"data:image/jpeg;base64,{0}",
        "imu_on": True
    }


@app.get("/check-video-connection")
async def check_video_connection():
    global test_result
    global current_case
    test_result = current_case['route'] == f'/check-video-connection'
    print(f'API called: /check-video-connection')
    await manager.broadcast(json.dumps({"result": test_result}))
    return {"connected": True}
    
@app.get("/check-tilt-sensor")
async def check_tilt_sensor():
    test_result = current_case['route'] == f'/check-tilt-sensor'
    print(f'API called: /check-tilt-sensor')
    await manager.broadcast(json.dumps({"result": test_result}))
    return {"connected": True}

@app.post("/run2")
async def start_processing():
    test_result = current_case['route'] == f'/run2'
    print(f'API called: /run2')
    await manager.broadcast(json.dumps({"result": test_result}))
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


@app.post("/csv")
async def csv(request: Request):
    global csvf
    dt = await request.json()
    csvf = dt
    pd.DataFrame.from_dict(data = dt, orient='index').to_csv('uitest.csv', header=False)
    return {"connected": True}

@app.get("/cases")
async def cases(request: Request):
    global test_case
    global group
    global page
    global csvf
    return {'files': test_case, 'page': page, 'group': group, 'record': csvf}

@app.get("/casedata/{p}/{g}/{c}")
async def cases(p, g, c):
    global current_case
    global group
    global page
    page = p
    group = g
    with open(f'ui_testdata/{p}/{g}/{c}.json', 'r') as f:
        current_case = json.load(f)

    return current_case
