import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import cv2
import json
import os
from datetime import datetime
import threading
import time
from be import ImageProcessingController

class TestImageProcessingController(unittest.TestCase):
    def setUp(self):
        # Create mock objects
        self.frame_grabber = MagicMock()
        self.analyze_box = MagicMock()  
        
        # Set up basic mocked logger
        self.frame_grabber.logger = MagicMock()
        
        # Create the controller
        self.controller = ImageProcessingController(self.frame_grabber, self.analyze_box)
        self.controller.viewmodel = MagicMock()
        # Set up test data directory
        self.test_dir = "test_exam_data"
        os.makedirs(self.test_dir, exist_ok=True)
        self.controller.exam_folder = self.test_dir

    def tearDown(self):
        # Clean up test directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Ensure process loop is stopped
        self.controller.is_running = False
        if hasattr(self, 'process_thread') and self.process_thread.is_alive():
            self.process_thread.join(timeout=1.0)

    def test_normal_mode_successful_frame_processing(self):
        """Test successful frame processing in normal mode with AP view"""
        # Setup initial conditions
        self.controller.model.mode = 1  # Normal mode
        self.controller.current_stage = 1
        self.controller.current_frame = 1
        self.controller.viewmodel.current_attempt = True
        self.controller.model.is_processing = False 
        self.controller.calib_data = {}

        # Create a mock frame
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)  # Black image
        self.frame_grabber._is_new_frame_available = True
        self.frame_grabber.fetchFrame.return_value = mock_frame
        
        # Mock analyze frame response
        self.controller.model.analyzeframe.return_value = (True, mock_frame, None)
        
        # Mock phantom analysis response
        phantom_result = (
            {"distortion_data": "test"},  # distort
            {"Reference": {"AP": {"ShotIndex": 0, "DistFile": "test.json"}}},  # camcalib
            mock_frame  # image
        )
        self.controller.model.analyze_phantom.return_value = (True, phantom_result, None)
        
        # Mock landmark analysis
        self.controller.model.analyze_landmark.return_value = (True, {"landmarks": "test"}, None)
        
        # Start the process loop in a separate thread
        self.controller.is_running = True
        self.process_thread = threading.Thread(target=self.controller._process_loop)
        self.process_thread.start()
        
        # Wait a short time for processing to occur
        #time.sleep(1)
        
        # Stop the processing
        self.controller.is_running = False
        self.process_thread.join(timeout=3.0)
            
        # Verify the basic flow
        self.frame_grabber.fetchFrame.assert_called()
        self.controller.model.analyzeframe.assert_called()
        self.controller.viewmodel.set_frame.return_value = ()
        self.controller.model.analyze_phantom.assert_called()
        self.controller.model.analyze_landmark.assert_called()
        
        # Verify stage/frame progression
        self.assertEqual(self.controller.current_frame, 2)
        self.assertEqual(self.controller.current_stage, 1)
    '''
    def test_simulation_mode_with_mock_data(self):
        """Test processing in simulation mode with mock image data"""
        # Setup simulation mode
        self.controller.model.mode = 0  # Simulation mode
        self.controller.current_stage = 1
        self.controller.current_frame = 1
        
        # Create mock image data
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_metadata = {"test": "metadata"}
        self.controller.mockdata = [
            {'img': mock_image, 'metadata': mock_metadata}
        ]
        self.controller.process_next_frame = True
        
        # Mock analyze frame response
        self.controller.model.analyzeframe.return_value = (True, mock_image, None)
        
        # Mock phantom analysis
        phantom_result = (
            {"distortion_data": "test"},
            {"Reference": {"AP": {"ShotIndex": 0, "DistFile": "test.json"}}},
            mock_image
        )
        self.controller.model.analyze_phantom.return_value = (True, phantom_result, None)
        
        # Mock landmark analysis
        self.controller.model.analyze_landmark.return_value = (True, {"landmarks": "test"}, None)
        
        # Start the process loop in a separate thread
        self.controller.is_running = True
        self.process_thread = threading.Thread(target=self.controller._process_loop)
        self.process_thread.start()
        
        
        # Stop the processing
        self.controller.is_running = False
        self.process_thread.join(timeout=0.5)
        
        # Verify simulation specific behavior
        self.assertEqual(len(self.controller.mockdata), 0)  # Mock data should be consumed
        self.assertFalse(self.controller.process_next_frame)  # Should be reset to False
        
        # Verify processing flow
        self.controller.model.analyzeframe.assert_called()
        self.controller.model.analyze_phantom.assert_called()
        self.controller.model.analyze_landmark.assert_called()
        
        # Verify stage/frame progression
        self.assertEqual(self.controller.current_frame, 2)
        self.assertEqual(self.controller.current_stage, 1)
    '''
if __name__ == '__main__':
    unittest.main()