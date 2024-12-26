import cv2
import numpy as np
import time
import threading

class AnalyzeBox:
    def __init__(self):
        self._stitch_progress = 0
        self._lock = threading.Lock()
        self._result = None

    @property
    def stitch_progress(self):
        """Returns the current progress (0-100) of the stitch operation."""
        with self._lock:
            return self._stitch_progress

    def crop_center(self, frame, target_size=700):
        """
        Crop the input frame to keep the central square region.
        
        Args:
        frame (numpy.ndarray): Input image frame
        target_size (int): Size of the square crop (default: 700)
        
        Returns:
        numpy.ndarray: Cropped image
        """
        height, width = frame.shape[:2]
        start_x = max(0, width // 2 - target_size // 2)
        start_y = max(0, height // 2 - target_size // 2)
        cropped = frame[start_y:start_y+target_size, start_x:start_x+target_size]
        return cropped

    def stitch(self, frame1, frame2):
        """
        Start the stitching process in a separate thread.
        
        Args:
        frame1 (numpy.ndarray): First input image frame
        frame2 (numpy.ndarray): Second input image frame
        """
        
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

    def get_result(self):
        """
        Get the result of the stitching operation.
        
        Returns:
        numpy.ndarray or None: The stitched image if completed, None if still processing
        """
        with self._lock:
            return self._result


def main():
    analyze_box = AnalyzeBox()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return
    
    ret1, frame1 = cap.read()
    ret2, frame2 = cap.read()
    cap.release()
    
    if not ret1 or not ret2:
        print("Error: Could not read frames.")
        return
    
    cropped_frame1 = analyze_box.crop_center(frame1)
    cropped_frame2 = analyze_box.crop_center(frame2)
    
    print("Starting stitch operation...")
    
    try:
        # Start the stitching process
        analyze_box.stitch(cropped_frame1, cropped_frame2)
        
        # Monitor and display progress while stitching
        while analyze_box.is_stitching:
            print(f"Stitching progress: {analyze_box.stitch_progress}%")
            time.sleep(0.5)
        
        print(f"Stitching completed: {analyze_box.stitch_progress}%")
        
        # Get the result
        stitched_frame = analyze_box.get_result()
        
        if stitched_frame is not None:
            cv2.imshow("Original Frame 1", frame1)
            cv2.imshow("Original Frame 2", frame2)
            cv2.imshow("Cropped Frame 1", cropped_frame1)
            cv2.imshow("Cropped Frame 2", cropped_frame2)
            cv2.imshow("Stitched Frame", stitched_frame)
            
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()