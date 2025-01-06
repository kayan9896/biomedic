import cv2
import numpy as np
import time
import threading

class AnalyzeBox:
    def __init__(self):
        self._stitch_progress = 0
        self._lock = threading.Lock()
        self._result = None
        self.images = [[None]*4, [None]*2, [None]*2]  # Initialize with proper structure
        self.stitched_result = [None]*2  # For rhp results
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

    def rhp(self, i):
        """Stitch horizontal pairs of images."""
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
            self._result = None
        
        try:
            result = self.stitch(self.images[0][i*2], self.images[0][i*2+1])
            self.stitched_result[i] = result
            return result
        finally:
            with self._lock:
                self._is_processing = False

    def rwp(self):
        """Stitch two rhp results vertically."""
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
            self._result = None
        
        def stitch_worker():
            try:
                # Vertical stitch of the two horizontal pairs
                if self.stitched_result[0] is not None and self.stitched_result[1] is not None:
                    self._result = np.vstack((self.stitched_result[0], self.stitched_result[1]))
                    
            finally:
                with self._lock:
                    self._is_processing = False
        
        self._stitch_thread = threading.Thread(target=stitch_worker)
        self._stitch_thread.start()
        self._stitch_thread.join()
        return self._result

    def analyzecup(self):
        """Analyze cup images at stage 2."""
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
        
        try:
            if self.images[1][0] is not None and self.images[1][1] is not None:
                result = self.stitch(self.images[1][0], self.images[1][1])
                return True, result, None
            return False, None, "Missing images for cup analysis"
        except Exception as e:
            return False, None, str(e)
        finally:
            with self._lock:
                self._is_processing = False

    def analyzetrial(self):
        """Analyze trial images at stage 3."""
        with self._lock:
            self._is_processing = True
            self._stitch_progress = 0
        
        try:
            if self.images[2][0] is not None and self.images[2][1] is not None:
                result = self.stitch(self.images[2][0], self.images[2][1])
                return True, result, None
            return False, None, "Missing images for trial analysis"
        except Exception as e:
            return False, None, str(e)
        finally:
            with self._lock:
                self._is_processing = False

    def analyzeframe(self, current_stage, current_frame, frame, target_size=700):
        """Analyze and store a single frame."""
        try:
            height, width = frame.shape[:2]
            start_x = max(0, width // 2 - target_size // 2)
            start_y = max(0, height // 2 - target_size // 2)
            cropped = frame[start_y:start_y+target_size, start_x:start_x+target_size]
            self.images[current_stage-1][current_frame-1] = cropped
            meta={}
            meta['curves'] = [
            [(x,x*x) for x in range(10)],
            [(x,x**3) for x in range(10)]]
            meta['points'] = [(50,50),(50,80)]
            return True, cropped, meta
        except Exception as e:
            return False, str(e)

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