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
        distance = int(self.sensor.distance * 100)
        self.handle_distance(distance)
       

    def cleanup(self):
        self.sensor.close()

    def handle_distance(self, distance):
        if distance < 20:
            message = f"Distance: {distance} cm - Hi!"
            self.send_message(data = message)
        elif distance > 30:
            message = f"Distance: {distance} cm - Bye!"
            self.send_message(data = message)