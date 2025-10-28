import unittest
from unittest.mock import MagicMock, patch
from imu import IMU_sensor
import time
import math

# Assuming IMU_sensor is imported from your module
# from your_module import IMU_sensor

class MockHandler:
    def __init__(self):
        self.tilt = None
        self.rotation = None

    def set_tilt(self, a):
        self.tilt = a

    def set_rotation(self, a):
        self.rotation = a

class MockPanel:
    def __init__(self):
        self.is_connected = True
        self.battery_level = 85
        self.tilt_angle = 10.0
        self.rotation_angle = 5.0
        self.noise = 0.5

class TestIMUSensorSimulation(unittest.TestCase):
    def setUp(self):
        self.handler = MockHandler()
        self.panel = MockPanel()
        self.imu = IMU_sensor(port=None, handler=self.handler, panel=self.panel, imu_simulation=True)
        

    @patch("threading.Thread")
    def test_start_simulation_mode(self):
        self.panel.is_connected = True
        result = self.imu.start(frequency=10.0)
        self.assertTrue(result)

        self.assertTrue(self.imu.is_connected)

    def test_check_tilt_sensor_connected(self):
        self.panel.is_connected = True
        self.panel.battery_level = 85
        result = self.imu.check_tilt_sensor()
        self.assertTrue(result["connected"])
        self.assertFalse(result["battery_low"])
        self.assertIn("connected successfully", result["message"])

    def test_check_tilt_sensor_low_battery(self):
        self.panel.is_connected = True
        self.panel.battery_level = 25
        result = self.imu.check_tilt_sensor()
        self.assertTrue(result["connected"])
        self.assertTrue(result["battery_low"])
        self.assertIn("battery is low", result["message"])

    def test_check_tilt_sensor_disconnected(self):
        self.panel.is_connected = False
        result = self.imu.check_tilt_sensor()
        self.assertFalse(result["connected"])
        self.assertIn("disconnected", result["message"])

    def test_set_tilt_and_rotation(self):
        self.imu.set_tilt(15.0)
        self.imu.set_rotation(30.0)
        self.assertEqual(self.imu.tilt_angle, 15.0)
        self.assertEqual(self.imu.rotation_angle, 30.0)
        self.assertEqual(self.handler.tilt, 15.0)
        self.assertEqual(self.handler.rotation, 30.0)

if __name__ == "__main__":
    unittest.main()