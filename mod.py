from typing import List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class SubAttempt:
    """Represents images for a single sub-attempt within a stage"""
    image1: Optional[np.ndarray] = None
    image2: Optional[np.ndarray] = None
    stitch: Optional[np.ndarray] = None

@dataclass
class Stage:
    """Represents a processing stage with its sub-attempts"""
    sub_attempts: List[SubAttempt] = None
    
    def __post_init__(self):
        if self.sub_attempts is None:
            self.sub_attempts = [SubAttempt(), SubAttempt()]  # Two sub-attempts for stage 1

@dataclass
class ProcessingAttempt:
    """Represents a complete processing attempt with all stages"""
    stages: List[Stage] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.stages is None:
            # Initialize three stages
            self.stages = [
                Stage(sub_attempts=[SubAttempt(), SubAttempt()]),  # Stage 1: two sub-attempts
                Stage(sub_attempts=[SubAttempt()]),                # Stage 2: one sub-attempt
                Stage(sub_attempts=[SubAttempt()])                 # Stage 3: one sub-attempt
            ]

class ProcessingModel:
    def __init__(self, max_attempts: int = 10):
        self.attempts: List[ProcessingAttempt] = []
        self.max_attempts = max_attempts
        self.current_attempt: Optional[ProcessingAttempt] = None
    
    def new_attempt(self) -> None:
        """Start a new processing attempt."""
        import time
        self.current_attempt = ProcessingAttempt(timestamp=time.time())
        self.attempts.append(self.current_attempt)
        
        if len(self.attempts) > self.max_attempts:
            self.attempts.pop(0)
    
    def set_image(self, stage: int, sub_attempt: int, frame: int, image: np.ndarray) -> None:
        """Set an image for the current attempt."""
        if self.current_attempt and 0 <= stage < len(self.current_attempt.stages):
            stage_obj = self.current_attempt.stages[stage]
            if 0 <= sub_attempt < len(stage_obj.sub_attempts):
                if frame == 1:
                    stage_obj.sub_attempts[sub_attempt].image1 = image
                elif frame == 2:
                    stage_obj.sub_attempts[sub_attempt].image2 = image
    
    def set_stitch_result(self, stage: int, sub_attempt: int, image: np.ndarray) -> None:
        """Set a stitched result for the current attempt."""
        if self.current_attempt and 0 <= stage < len(self.current_attempt.stages):
            stage_obj = self.current_attempt.stages[stage]
            if 0 <= sub_attempt < len(stage_obj.sub_attempts):
                stage_obj.sub_attempts[sub_attempt].stitch = image
        
    def get_attempt(self, index: int = -1) -> Optional[ProcessingAttempt]:
        """
        Get a specific attempt by index.

        :param index: Index of the attempt. -1 for the latest attempt.
        :return: The requested ProcessingAttempt or None if not found.
        """
        try:
            return self.attempts[index]
        except IndexError:
            return None
    
    def clear(self) -> None:
        """Clear all attempts."""
        self.attempts.clear()
        self.current_attempt = None