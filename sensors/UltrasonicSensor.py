from gpiozero import DistanceSensor
from sensors.BaseSensor import BaseSensor
from dataclass import UltrasonicConfig
import time

class UltrasonicSensor(BaseSensor):
    def __init__(self, 
                 service_name = "DistanceSensor", 
                 message_queue = None,
                 debug = False,
                 config: UltrasonicConfig = None):
        config = config or UltrasonicConfig()
        super().__init__(service_name, message_queue, config, debug)
        
        self.sensor = DistanceSensor(
            echo = config.echo_pin,
            trigger = config.trigger_pin,
            max_distance = config.max_distance
        )
    
    def setup(self):
        if self.debug:
            self._logger.info("Time to debug")

    def loop(self):
        try:
            while not self._stop_event.is_set():
                distance = self.sensor.distance
                if distance is not None:
                    distance_cm = int(distance * 100)
                    self.handle_distance(distance_cm)
                time.sleep(0.1)
        except Exception as e:
            self._logger.error(f"Error reading distance: {e}")

        distance = int(self.sensor.distance * 100)
        self.handle_distance(distance)
       

    def cleanup(self):
        self.sensor.close()

    def handle_distance(self, distance):
        if distance < 100:
            self.send_message(data = distance)