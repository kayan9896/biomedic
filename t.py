from flask import Flask, jsonify
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/route1')from flask import Flask, Response
import json
from flask_cors import CORS
import threading
from libra import compute, progress_tracker

app = Flask(__name__)
CORS(app)

@app.route('/route1')
def route1():
    time.sleep(20)
    return {'result': 20}

@app.route('/route2')
def route2():
    return {'result': 0}

@app.route('/route3')
def route3():
    progress_tracker.update(0)  # Reset progress

    # Start computation in a separate thread
    thread = threading.Thread(target=compute)
    thread.start()

    # Wait for computation to complete
    thread.join()

    return {'result': 1}

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
def route1():
    time.sleep(20)  # Wait for 20 seconds
    return jsonify({"result": 20})

@app.route('/route2')
def route2():
    return jsonify({"result": 0})

if __name__ == '__main__':
    app.run(debug=True,threaded=False)