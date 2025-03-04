from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np
import cv2

@dataclass
class Frame:
    """Represents a single frame with its image and metadata"""
    image: Optional[np.ndarray] = None
    metadata: dict = field(default_factory=dict)

    def draw_ellipse_from_metadata(self, img, ellipse_data):
        """
        Draw an ellipse based on two vertices and one point on the ellipse.
        ellipse_data: Dictionary containing 'end1', 'end2', and 'pointOnEllipse' coordinates
        """
        # Extract points
        end1 = np.array([ellipse_data[0][0], ellipse_data[1][1]])
        end2 = np.array([ellipse_data[2][0], ellipse_data[2][1]])
        point_on_ellipse = np.array([ellipse_data[1][0], ellipse_data[1][1]])
        
        # Calculate center
        center = ((end1 + end2) / 2).astype(int)
        
        # Calculate major axis - distance between the two ends
        major_axis_length = np.linalg.norm(end2 - end1) / 2
        
        # Calculate angle of rotation (in degrees)
        dx = end2[0] - end1[0]
        dy = end2[1] - end1[1]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Vector from center to point on ellipse
        vec_to_point = point_on_ellipse - center
        
        # Rotate this vector back by -angle to get it in the ellipse's coordinate system
        angle_rad = np.radians(-angle)
        rot_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])
        rotated_vec = rot_matrix.dot(vec_to_point)
        
        # The y-coordinate in this rotated space gives us the minor axis
        minor_axis_length = abs(rotated_vec[1])
        
        # Convert to integer values for OpenCV
        center_tuple = tuple(center)
        axes_lengths = (int(major_axis_length), int(minor_axis_length))
        
        # Draw the ellipse
        cv2.ellipse(img, center_tuple, axes_lengths, angle, 0, 360, (0, 255, 0), 2)

    def generate_image_with_overlays(self):
        def ellipse_from_vertices_and_point(v1, v2, p):
            """
            Convert two vertices and a point on ellipse to parameters needed for drawing
            
            Args:
                v1, v2: Two vertices that form one axis of the ellipse (dict with 0 and 1)
                p: A point on the ellipse (dict with 0 and 1)
            
            Returns:
                Dictionary with parameters for drawing
            """
            # Convert dictionaries to numpy arrays for easier calculation
            v1_arr = np.array([v1[0], v1[1]])
            v2_arr = np.array([v2[0], v2[1]])
            p_arr = np.array([p[0], p[1]])
            
            # 1. Calculate center
            center = (v1_arr + v2_arr) / 2
            
            # 2. Calculate first axis length (half the distance between vertices)
            axis1_length = np.linalg.norm(v2_arr - v1_arr) / 2
            
            # 3. Calculate direction vector of first axis
            axis1_dir = (v2_arr - v1_arr) / np.linalg.norm(v2_arr - v1_arr)
            
            # 4. Calculate rotation angle (in degrees)
            angle_rad = np.arctan2(axis1_dir[1], axis1_dir[0])
            angle_deg = np.degrees(angle_rad)
            
            # 5. Project the point p onto the main axis to find component parallel to axis1
            p_centered = p_arr - center
            proj_on_axis1 = np.dot(p_centered, axis1_dir) * axis1_dir
            
            # 6. Find the component perpendicular to axis1
            perp_component = p_centered - proj_on_axis1
            
            # 7. Calculate second axis length based on the ellipse equation
            # If point is on ellipse: (x/a)² + (y/b)² = 1, where a and b are semi-axes lengths
            if np.linalg.norm(proj_on_axis1) > 0:
                axis2_length = axis1_length * np.linalg.norm(perp_component) / np.linalg.norm(proj_on_axis1)
            else:
                # Handle special case
                axis2_length = np.linalg.norm(perp_component)
            
            return {
                'center': (int(center[0]), int(center[1])),
                'axes': (int(axis1_length), int(axis2_length)),
                'angle': angle_deg,
                'startAngle': 0,
                'endAngle': 360
            }

        # Example of how to use with OpenCV
        def draw_ellipse_on_image(image, ellipse_params, color=(0, 255, 0), thickness=2):
            cv2.ellipse(
                image,
                ellipse_params['center'],
                ellipse_params['axes'],
                ellipse_params['angle'],
                ellipse_params['startAngle'],
                ellipse_params['endAngle'],
                color,
                thickness
            )
            return image
        if self.image is None:
            return None
        
        # Create a copy of the image to avoid modifying the original
        img_with_overlays = self.image.copy()
        
        # Draw circle if present in metadata
        if 'circle' in self.metadata:
            circle = self.metadata['circle']
            center = (int(circle['center'][0]), int(circle['center'][1]))
            edge = (int(circle['edgePoint'][0]), int(circle['edgePoint'][1]))
            radius = int(np.sqrt((center[0] - edge[0])**2 + (center[1] - edge[1])**2))
            cv2.circle(img_with_overlays, center, radius, (0, 255, 0), 2)
        
        if 'ellipse' in self.metadata:
            ellipse = self.metadata['ellipse']
            v1 = ellipse[0]
            v2 = ellipse[2]
            point_on_ellipse = ellipse[1]
            
            params = ellipse_from_vertices_and_point(v1, v2, point_on_ellipse)
            draw_ellipse_on_image(img_with_overlays, params)
            
        # Draw lines if present
        if 'lines' in self.metadata:
            lines = self.metadata['lines']
            if 'straight' in lines:
                points = lines['straight']
                for i in range(len(points) - 1):
                    pt1 = (int(points[i][0]), int(points[i][1]))
                    pt2 = (int(points[i+1][0]), int(points[i+1][1]))
                    cv2.line(img_with_overlays, pt1, pt2, (0, 0, 255), 2)
        
        cv2.imwrite('img.png', img_with_overlays)

@dataclass
class Stage:
    """Represents a stage with its frames and stitched result"""
    frames: List[Frame]
    stitched: Optional[np.ndarray] = None

@dataclass
class ProcessingAttempt:
    """Represents a complete processing attempt with all stages"""
    stages: List[Stage]
    timestamp: float = 0.0

    def __init__(self):
        import time
        self.stages = [
            Stage(frames=[Frame() for _ in range(4)]),  # Stage 1: 4 frames
            Stage(frames=[Frame() for _ in range(2)]),  # Stage 2: 2 frames
            Stage(frames=[Frame() for _ in range(2)])   # Stage 3: 2 frames
        ]
        self.timestamp = time.time()

class ProcessingModel:
    def __init__(self, max_attempts: int = 10):
        self.attempts: List[ProcessingAttempt] = []
        self.max_attempts = max_attempts
        self.current_attempt: Optional[ProcessingAttempt] = None
        self.states = {
            'angle': 0,
            'rotation_angle': 0,
            'img_count': 0,  
            'is_processing': False,
            'progress': 0,
            'ap_carm': False,
            'ob_carm': False,
            'imu_on': True,
            'video_on':True,
            'carm_moving':False,#optional
            'current_stage': 1,#optional
            'current_frame': 1#optional
        }
        self.imgs = [{'image': None, 'metadata': None, 'checkmark': None, 'error': None, 'next': False} for i in range(2)]

    def update(self, dataforvm, image):
        # Assuming dataforvm contains metadata
        
        angle = self.states['rotation_angle']
        if -15 <= angle <= 15:
            if image is not None: self.imgs[0]['image'] = image
            for i in dataforvm:
                self.imgs[0][i] = dataforvm[i]
        elif -45 <= angle <= 45:
            if image is not None: self.imgs[1]['image'] = image
            for i in dataforvm:
                self.imgs[1][i] = dataforvm[i]
        
        self.update_img_count()

    def store_frame(self, frame, angle):
        """Store frame based on angle conditions and update img_count"""
        if -15 <= angle <= 15:
            self.imgs[0] = frame
            self.update_img_count()
        elif -45 <= angle <= 45:
            self.imgs[1] = frame
            self.update_img_count()
        # If angle is outside [-45, 45], frame is discarded and img_count not updated

    def update_img_count(self):
        """Update img_count cycling from 0 to 4"""
        current_count = self.states['img_count']
        self.states['img_count'] = (current_count + 1) % 5

    def update_state(self, key: str, value: any):
        """Update a specific state value"""
        self.states[key] = value

    def get_states(self):
        """Get all states"""
        return self.states
    
    def new_attempt(self) -> None:
        self.current_attempt = ProcessingAttempt()
        self.attempts.append(self.current_attempt)
        if len(self.attempts) > self.max_attempts:
            self.attempts.pop(0)
    
    def set_frame(self, stage: int, frame: int, image: np.ndarray, metadata: dict = None) -> None:
        """Set a specific frame image and metadata"""
        if self.current_attempt and 1 <= stage <= 3:
            stage_idx = stage - 1
            frame_idx = frame - 1
            self.current_attempt.stages[stage_idx].frames[frame_idx].image = image
            if metadata:
                self.current_attempt.stages[stage_idx].frames[frame_idx].metadata = metadata
    
    def get_frame_metadata(self, attempt_idx: int, stage: int, frame: int) -> dict:
        """Get metadata for a specific frame"""
        try:
            attempt = self.attempts[attempt_idx]
            return attempt.stages[stage-1].frames[frame-1].metadata
        except (IndexError, AttributeError):
            return {}
    
    def set_stitched(self, stage: int, image: np.ndarray) -> None:
        """Set the stitched result for a specific stage"""
        if self.current_attempt and 1 <= stage <= 3:
            stage_idx = stage - 1
            self.current_attempt.stages[stage_idx].stitched = image
    
    def get_attempt(self, index: int = -1) -> Optional[ProcessingAttempt]:
        try:
            return self.attempts[index]
        except IndexError:
            return None



    