from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import math
from PIL import Image

app = Flask(__name__)
CORS(app)

# Sample initial points
points = [
    {"x": 100, "y": 100},
    {"x": 200, "y": 200},
    {"x": 150, "y": 300}
]

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt(
        (point2["x"] - point1["x"]) ** 2 + 
        (point2["y"] - point1["y"]) ** 2
    )

def calculate_all_distances(points):
    """Calculate distances between consecutive points"""
    distances = []
    for i in range(len(points) - 1):
        distance = calculate_distance(points[i], points[i + 1])
        distances.append(round(distance))
    return distances

@app.route('/api/points', methods=['GET'])
def get_points():
    """Return all points and their distances"""
    distances = calculate_all_distances(points)
    return jsonify({
        "points": points,
        "distances": distances
    })

@app.route('/api/points/update', methods=['POST'])
def update_points():
    """Update point coordinates and return new distances"""
    global points
    new_points = request.json.get('points')
    if new_points:
        points = new_points
        distances = calculate_all_distances(points)
        return jsonify({
            "points": points,
            "distances": distances
        })
    return jsonify({"error": "Invalid points data"}), 400

@app.route('/api/scan-image', methods=['GET'])
def get_scanned_image():
    # Code to interact with the scanner and get the image
    # This is pseudo-code and will depend on your scanner's API
    img_io=Image.open('bio/src/gf.gif') 
    
    
    return send_file('bio/src/gf.gif', mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True)