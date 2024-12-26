from typing import List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class ProcessingAttempt:
    """
    Represents a single processing attempt with its associated images.
    """
    first_cropped_image: Optional[np.ndarray] = None
    second_cropped_image: Optional[np.ndarray] = None
    stitched_result: Optional[np.ndarray] = None
    timestamp: float = 0.0  # Time when the attempt was created

class ProcessingModel:
    """
    Manages multiple processing attempts and their associated images.
    """
    def __init__(self, max_attempts: int = 10):
        """
        Initialize the ProcessingModel.

        :param max_attempts: Maximum number of attempts to store before discarding old ones.
        """
        self.attempts: List[ProcessingAttempt] = []
        self.max_attempts = max_attempts
        self.current_attempt: Optional[ProcessingAttempt] = None
    
    def new_attempt(self) -> None:
        """
        Start a new processing attempt.
        """
        import time
        self.current_attempt = ProcessingAttempt(timestamp=time.time())
        self.attempts.append(self.current_attempt)
        
        # Remove old attempts if we've exceeded the maximum
        if len(self.attempts) > self.max_attempts:
            self.attempts.pop(0)
    
    def set_first_image(self, image: np.ndarray) -> None:
        """Set the first cropped image for the current attempt."""
        if self.current_attempt:
            self.current_attempt.first_cropped_image = image
    
    def set_second_image(self, image: np.ndarray) -> None:
        """Set the second cropped image for the current attempt."""
        if self.current_attempt:
            self.current_attempt.second_cropped_image = image
    
    def set_stitched_result(self, image: np.ndarray) -> None:
        """Set the stitched result for the current attempt."""
        if self.current_attempt:
            self.current_attempt.stitched_result = image
    
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