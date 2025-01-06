from typing import List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class Stage:
    """Represents a stage with its frames and stitched result"""
    frames: List[Optional[np.ndarray]]  # List to store frame images
    stitched: Optional[np.ndarray] = None

@dataclass
class ProcessingAttempt:
    """Represents a complete processing attempt with all stages"""
    stages: List[Stage]
    timestamp: float = 0.0

    def __init__(self):
        import time
        self.stages = [
            Stage(frames=[None, None, None, None]),  # Stage 1: 4 frames
            Stage(frames=[None, None]),              # Stage 2: 2 frames
            Stage(frames=[None, None])               # Stage 3: 2 frames
        ]
        self.timestamp = time.time()

class ProcessingModel:
    def __init__(self, max_attempts: int = 10):
        self.attempts: List[ProcessingAttempt] = []
        self.max_attempts = max_attempts
        self.current_attempt: Optional[ProcessingAttempt] = None
    
    def new_attempt(self) -> None:
        self.current_attempt = ProcessingAttempt()
        self.attempts.append(self.current_attempt)
        if len(self.attempts) > self.max_attempts:
            self.attempts.pop(0)
    
    def set_frame(self, stage: int, frame: int, image: np.ndarray) -> None:
        """Set a specific frame image"""
        if self.current_attempt and 1 <= stage <= 3:
            print(stage,frame,image)
            stage_idx = stage - 1
            frame_idx = frame - 1
            self.current_attempt.stages[stage_idx].frames[frame_idx] = image
            print(self.attempts)
    
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