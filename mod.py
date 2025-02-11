from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np

@dataclass
class Frame:
    """Represents a single frame with its image and metadata"""
    image: Optional[np.ndarray] = None
    metadata: dict = field(default_factory=dict)

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
            'img_count': 0,  # Add img_count to states
            'is_processing': False,
            'current_stage': 1,
            'current_frame': 1
        }
        self.imgs = [None, None]

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



    