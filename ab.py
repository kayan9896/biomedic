import cv2
import numpy as np
import time
import threading

class AnalyzeBox:
    def __init__(self):
        self._stitch_progress = 0
        self._lock = threading.Lock()
        self._result = None
        self._first_image = None
        self._second_image = None
        self._is_processing = False
        self._stitch_thread = None

    @property
    def is_processing(self):
        """Returns whether the AnalyzeBox is currently processing (storing images or stitching)."""
        with self._lock:
            return self._is_processing

    @property
    def stitch_progress(self):
        """Returns the current progress (0-100) of the stitch operation."""
        with self._lock:
            return self._stitch_progress

    def process_frame(self, frame, model):
        """
        Process a new frame: store it as first or second image, or start stitching.
        
        Args:
        frame (numpy.ndarray): New frame to process
        model (ProcessingModel): Model to store the results
        """
        with self._lock:
            if self._is_processing:
                return  # Skip this frame if we're already processing

            cropped_frame = self.crop_center(frame)
            current_attempt = model.current_attempt

            if current_attempt.first_cropped_image is None:
                model.set_first_image(cropped_frame)
                self._first_image = cropped_frame
            elif current_attempt.second_cropped_image is None:
                model.set_second_image(cropped_frame)
                self._second_image = cropped_frame
        
        if self._second_image is not None:
            self._start_stitch(model)

    def _start_stitch(self, model):
        """
        Start the stitching process in a separate thread.
        
        Args:
        model (ProcessingModel): Model to store the result
        """
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
            self._result = None
        
        def stitch_worker():
            try:
                result = self.stitch(self._first_image, self._second_image)
                model.set_stitched_result(result)
            finally:
                with self._lock:
                    self._is_processing = False
                    self._first_image = None
                    self._second_image = None
        
        self._stitch_thread = threading.Thread(target=stitch_worker)
        self._stitch_thread.start()

    def crop_center(self, frame, target_size=700):
        """Crop the input frame to keep the central square region."""
        height, width = frame.shape[:2]
        start_x = max(0, width // 2 - target_size // 2)
        start_y = max(0, height // 2 - target_size // 2)
        cropped = frame[start_y:start_y+target_size, start_x:start_x+target_size]
        return cropped

    def stitch(self, frame1, frame2):
        """Stitch two frames together."""
        if frame1.shape[0] != frame2.shape[0]:
            max_height = max(frame1.shape[0], frame2.shape[0])
            frame1_resized = cv2.resize(frame1, (int(frame1.shape[1] * max_height / frame1.shape[0]), max_height))
            frame2_resized = cv2.resize(frame2, (int(frame2.shape[1] * max_height / frame2.shape[0]), max_height))
        else:
            frame1_resized, frame2_resized = frame1, frame2

        # Simulate processing with progress updates
        k=0
        for i in range(10000):
            for j in range(3000):
                with self._lock:
                    self._stitch_progress = (k + 1) /300000
                    k+=1

        # Stitch the images
        self._result = np.hstack((frame1_resized, frame2_resized))
        return self._result