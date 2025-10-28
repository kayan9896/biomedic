import pytest
from unittest.mock import MagicMock, patch

from imu import IMU_sensor

class MockHandler:
    def __init__(self):
        self.tilt = None
        self.rotation = None

    def set_tilt(self, a):
        self.tilt = a

    def set_rotation(self, a):
        self.rotation = a

@pytest.fixture
def imu_sensor():
    handler = MockHandler()
    panel = MagicMock()  # Not used in hardware mode
    return IMU_sensor(port=None, handler=handler, panel=panel, imu_simulation=False)

@patch("openzen.make_client")
@patch("openzen.ZenError.NoError", new=0)
@patch("openzen.ZenSensorInitError.NoError", new=0)
def test_start_hardware_mode(mock_make_client, imu_sensor):
    mock_client = MagicMock()
    mock_sensor_desc = MagicMock()
    mock_sensor = MagicMock()

    # Simulate sensor listing events
    events = [
        MagicMock(event_type=1, data=MagicMock(sensor_found=mock_sensor_desc)),
        MagicMock(event_type=2, data=MagicMock(sensor_listing_progress=MagicMock(progress=1.0, complete=1)))
    ]
    mock_client.wait_for_next_event.side_effect = lambda: events.pop(0) if events else None
    mock_client.list_sensors_async.return_value = 0
    mock_client.obtain_sensor.return_value = (0, mock_sensor)
    mock_make_client.return_value = (0, mock_client)

    with patch("threading.Thread") as mock_thread:
        result = imu_sensor.start(frequency=10.0)
        assert result is True
        assert imu_sensor.is_connected is True
        mock_thread.assert_called_once()

@patch("openzen.make_client")
def test_start_hardware_mode(mock_make_client, imu_sensor):
    mock_client = MagicMock()
    mock_poll = MagicMock(data=MagicMock(imu_data=MagicMock(r=[-5, 5])))

    mock_sensor_desc = MagicMock()
    mock_sensor = MagicMock()

    # Simulate sensor listing events
    events = [
        MagicMock(event_type=1, data=MagicMock(sensor_found=mock_sensor_desc)),
        MagicMock(event_type=2, data=MagicMock(sensor_listing_progress=MagicMock(progress=1.0, complete=1)))
    ]
    mock_client.wait_for_next_event.side_effect = lambda: events.pop(0) if events else None
    mock_client.list_sensors_async.return_value = 0
    mock_client.obtain_sensor.return_value = (0, mock_sensor)

    mock_client.poll_next_event.return_value = mock_poll
    mock_make_client.return_value = (0, mock_client)


    result = imu_sensor.start(frequency=10.0)
    assert result is True
    assert imu_sensor.is_connected is True
    
    assert imu_sensor.tilt_angle == -5
    assert imu_sensor.rotation_angle == 5
    imu_sensor.is_connected = False

@patch("openzen.make_client")
def test_sensor_connection_failure(mock_make_client, imu_sensor):
    mock_make_client.return_value = (1, None)  # Simulate error
    result = imu_sensor.start()
    assert isinstance(result, str)
    assert "Error starting imu" in result
    assert imu_sensor.is_connected is False

def test_set_tilt_and_rotation(imu_sensor):
    imu_sensor.set_tilt(12.5)
    imu_sensor.set_rotation(-7.3)
    assert imu_sensor.handler.tilt == 12.5
    assert imu_sensor.handler.rotation == -7.3