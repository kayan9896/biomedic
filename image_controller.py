import math
import cv2
import time
import numpy as np
from PyQt5.QtCore import QTimer

cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video stream or file")
    exit()


class ImageController:  
    def __init__(self, view):
        self.view = view
        self.image1_path = 'C:/Users/A4ssg/Downloads/fr.png'
        self.image2_path = 'C:/Users/A4ssg/Downloads/heatmap.png'
        self.current_image_path = self.image1_path
        self.state = 1
        
        self.sample_coords = [
            [(100, 100), (200, 150), (300, 200)],
            [(400, 100), (450, 200), (500, 150)],
            [(i,i**1.1) for i in range(1,200,20)],
            [(i,math.log(i)) for i in range(1,200,20)]
        ]
        
    def take(self):
        if self.state == 0:
            ret, frame = cap.read()
            
            if not ret:
                print("Failed to grab frame")
                return
            
            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY_INV, 11, 2)

            # Apply morphological operations to remove noise
            kernel = np.ones((5,5),np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            spot_coordinates = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:  # Adjust this value based on your needs
                    M = cv2.moments(contour)
                    if M['m00'] != 0:
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])
                        spot_coordinates.append((cx, cy))
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

            # Update the view with the processed frame
            self.view.load_image(frame)
            
            # Update the detected coordinates
            self.update_detected_coordinates(spot_coordinates)
            
            # Start a timer to capture the next frame after a certain interval
            QTimer.singleShot(100, self.take)

    def update_detected_coordinates(self, coordinates):
        # This method should be implemented to update your view or model
        # with the detected coordinates
        print("Detected coordinates:", coordinates)
        # You might want to store these coordinates or update the view
        # For example:
        # self.view.update_coordinates(coordinates)
        
    def load_current_image(self):
        self.view.load_image(self.current_image_path)
        
    def toggle_image(self):
        self.state+=1
        self.state%=3
        self.view.clear_all_points()
        if self.state==1:
            self.view.load_image(self.image1_path)
        elif self.state==2:
            self.view.load_image(self.image2_path)
        else:
            self.take()
        

    def add_sample_curve(self):
        self.view.clear_all_points()
        for curve_points in self.sample_coords:
            self.view.add_curve_points(curve_points)
        self.update_distances()

    def calculate_distance(self, p1, p2):
        """Calculate the Euclidean distance between two points."""
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def update_distances(self):
        """Calculate distances for all curves and update the view."""
        all_distances = []
        for curve in self.view.get_curve_coordinates():
            curve_distances = []
            for i in range(len(curve) - 1):
                distance = self.calculate_distance(curve[i], curve[i+1])
                curve_distances.append(distance)
            all_distances.append(curve_distances)
        
        self.view.update_distance_labels(all_distances)