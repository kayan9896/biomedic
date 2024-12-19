import time
import random
from threading import Lock

class ComputationProgress:
    def __init__(self):
        self.progress = 0
        self.lock = Lock()

    def update(self, progress):
        with self.lock:
            self.progress = progress

    def get(self):
        with self.lock:
            return self.progress

progress_tracker = ComputationProgress()

def compute():
    total_steps = 100  # Let's say our computation has 100 steps
    for step in range(total_steps):
        # Simulate some work
        time.sleep(random.uniform(0.13, 0.19))

        # Update progress
        progress = int((step + 1) / total_steps * 100)
        progress_tracker.update(progress)

    return 1