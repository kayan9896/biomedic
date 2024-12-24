from flask import Flask, Response
import time
import json
from flask_cors import CORS
from libra import compute
import threading

app = Flask(__name__)
CORS(app)

# Global variable to store computation progress
computation_progress = 0

def background_computation():
    global computation_progress
    start_time = time.time()
    expected_duration = 6  # Average of 13 and 19 seconds

    # Start the actual computation in a separate thread
    result_thread = threading.Thread(target=compute)
    result_thread.start()

    while result_thread.is_alive():
        elapsed_time = time.time() - start_time
        computation_progress = min(95, int((elapsed_time / expected_duration) * 100))
        time.sleep(0.1)

    computation_progress = 100

@app.route('/route1')
def route1():
    time.sleep(20)
    return {'result': 20}

@app.route('/route2')
def route2():
    return {'result': 0}

@app.route('/route3')
def route3():
    global computation_progress
    computation_progress = 0

    # Start background computation
    thread = threading.Thread(target=background_computation)
    thread.start()

    res = compute()
    return {'result': res}

@app.route('/progress')
def progress():
    def generate():
        global computation_progress
        while computation_progress < 100:
            yield f"data: {json.dumps({'progress': computation_progress})}\n\n"
            time.sleep(0.1)
        yield f"data: {json.dumps({'progress': 100})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)