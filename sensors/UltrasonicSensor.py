import logging
import time
from gpiozero import DistanceSensor
from sensors.BaseSensor import BaseSensor
from dataclass.UltrasonicConfig import UltrasonicConfig

logger = logging.getLogger(__name__)

class UltrasonicSensor(BaseSensor):
    def __init__(self, 
                 service_name = "DistanceSensor", 
                 debug = False,
                 config: UltrasonicConfig = None):
        config = config or UltrasonicConfig()
        super().__init__(service_name, config, debug)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.config = config
        self.sensor = DistanceSensor(
            echo = config.echo_pin,
            trigger = config.trigger_pin,
            max_distance = config.max_distance
        )
    
    def setup(self):
        pass

    def loop(self):
        try:
            distance = self.sensor.distance
            
            if distance is not None:
                distance_cm = int(distance * 100)
                logger.debug(f"{distance_cm} cm")

                if distance_cm < self.config.threshold: 
                    scale_factor = self.config.threshold / distance_cm
                    message = self.config.level_steps * scale_factor
                    self.send_message(service_name = self.service_name,
                                        data = {
                                            "time": self.config.restoration_duration,
                                            "level_steps": message
                                        },
                                        queue=self.outgoing_queue)
                    time.sleep(self.config.restoration_duration)
            time.sleep(self.config.loop_refresh_rate)
            
        except Exception as e:
            logger.error(f"Error reading distance: {e}")
       
    def cleanup(self):
        self.sensor.close()