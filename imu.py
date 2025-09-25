import threading
import time
import logging
import math
import sys
sys.path.append("C:/")
import openzen

openzen.set_log_level(openzen.ZenLogLevel.Warning)

class IMU_sensor:
    def __init__(self, port, handler, panel, imu_simulation = False):
        self.tilt_angle = 0
        self.rotation_angle = 0
        self.is_connected = False
        self.battery_level = 100
        self.handler = handler
        self.panel = panel
        self.imu_simulation = imu_simulation
        self.sensor_desc_connect = None

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def start(self, frequency: float = 30.0):
        try:
            if not self.imu_simulation:
                error, self.client = openzen.make_client()
                if not error == openzen.ZenError.NoError:
                    print ("Error while initializing OpenZen library")

                error = self.client.list_sensors_async()
                while True:
                    zenEvent = self.client.wait_for_next_event()

                    if zenEvent.event_type == openzen.ZenEventType.SensorFound:
                        print ("Found sensor {} on IoType {}".format( zenEvent.data.sensor_found.name,
                            zenEvent.data.sensor_found.io_type))
                        if self.is_connected is False:
                            self.sensor_desc_connect = zenEvent.data.sensor_found
                            self.is_connected = self.sensor_desc_connect is not None 

                    if zenEvent.event_type == openzen.ZenEventType.SensorListingProgress:
                        lst_data = zenEvent.data.sensor_listing_progress
                        print ("Sensor listing progress: {} %".format(lst_data.progress * 100))
                        if lst_data.complete > 0:
                            break
                print ("Sensor Listing complete")
                error, self.sensor = self.client.obtain_sensor(self.sensor_desc_connect )
                if not error == openzen.ZenSensorInitError.NoError:
                    self.is_connected = False
                    print ("Error connecting to sensor")

            self.check_thread = threading.Thread(
                target=self.imu_loop,
                args=(frequency,),
                #daemon=True
            )
            self.check_thread.start()
            
            self.logger.info(f"Started imu checking at {frequency} Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting imu: {str(e)}")
            return f"Error starting imu: {str(e)}"

    def imu_loop(self, frequency: float):
        """Main loop for checking video frames"""
        period = 1.0 / frequency
        
        if not self.imu_simulation:
            
            t = time.time()
            while self.is_connected:
                zenEvent = self.client.poll_next_event()
                if zenEvent is None:
                    if time.time() - t > 5:
                        self.is_connected = False
                    continue
                #self.battery_level = self.sensor.get_float_property(openzen.ZenSensorProperty.BatteryLevel)[1]
                self.set_tilt(zenEvent.data.imu_data.r[0])
                self.set_rotation(zenEvent.data.imu_data.r[1])
                t = time.time()
                #print(zenEvent.data.imu_data.r)
            
        else:
            self.is_connected = self.panel.is_connected
            while self.is_connected:
                self.is_connected = self.panel.is_connected
                self.battery_level = self.panel.battery_level
                noise = self.panel.noise * math.sin(time.time()**2)
                self.set_tilt(self.panel.tilt_angle + noise)
                self.set_rotation(self.panel.rotation_angle + noise)
                time.sleep(period)

    def check_tilt_sensor(self):
        self.start()        
        if not self.is_connected:
            message = "Tilt sensor disconnected. Please check the connection."
        elif self.battery_level < 30:
            message = "Tilt sensor connected but battery is low. Consider replacing batteries soon."
        else:
            message = "Tilt sensor connected successfully."
        return {
            "connected": self.is_connected,
            "battery_low": self.battery_level < 30,
            "message": message
        }
    
    def set_tilt(self, a):
        self.tilt_angle = a
        self.handler.set_tilt(a)

    def set_rotation(self, a):
        self.rotation_angle = a
        self.handler.set_rotation(a)
    