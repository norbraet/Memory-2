import logging
from outputs.BaseOutput import BaseOutput
from dataclass.LedConfig import LedConfig
from gpiozero import PWMLED
from time import sleep

logger = logging.getLogger(__name__)

class LedOutput(BaseOutput):
    def __init__(self, service_name, config:LedConfig=None, debug=False):
        config = config or LedConfig()
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        super().__init__(service_name, config, debug)
        self.config = config
        self.red = None
        self.green = None
        self.blue = None

    def setup(self):
        logger.info(f"Setting up {self.service_name}")
        self.red = PWMLED(self.config.r_pin)
        self.green = PWMLED(self.config.g_pin)
        self.blue = PWMLED(self.config.b_pin)

        self._set_color(r = 0, g = 0, b = 0)

    def loop(self):
        """
        Process the incoming queue.
        """

        message = self.receive_message(queue=self.incoming_queue, block=True, timeout=None)
        data = message.data
        
        logger.info(f"LedOutput | Habe eine Nachricht empfangen: {message}")
        if isinstance(data, dict) and "distance" in data and "threshold" in data:
            distance = data["distance"]
            threshold = data["threshold"]
            duration = data.get("time", 1)

            r, g, b = self._calculate_led_color(distance_cm = distance, threshold = threshold)
            
            self._set_color(r=r, g=g, b=b)
            sleep(duration)
            self._set_color(r = 0, g = 0, b = 0)

            for test_distance in range(0, threshold + 1, 10):  
                 print(f"Distance: {test_distance} cm → Color: {self._calculate_led_color(test_distance, threshold)}")


    def trigger_action(self, data):
        pass
    
    def cleanup(self):
        """Clean up the led resources properly before shutdown."""

        logger.info(f"Cleaning up {self.service_name}")
        self._set_color(0, 0, 0)
        
        if self.red:
            self.red.close()
        if self.green:
            self.green.close()
        if self.blue:
            self.blue.close()

        self.red = None
        self.green = None
        self.blue = None

        

    def _set_color(self, r, g, b):
        """ Set the RGB LED color with values from 0 (off) to 1 (full brightness). """
        self.red.value = r
        self.green.value = g
        self.blue.value = b

    def _calculate_led_color(self, distance_cm, threshold):
        """
        Calculate LED color based on distance.
        
        - Close distance → Green (0,1,0)
        - Mid distance → Yellow (1,1,0)
        - Far distance (threshold) → Red (1,0,0)
        
        :param distance_cm: Measured distance in cm
        :param threshold: Maximum threshold distance in cm
        :return: (red, green, blue) tuple for LED color
        """

        distance_cm = max(0, min(distance_cm, threshold))
        # factor = distance_cm / threshold
        factor = 1 - (distance_cm / threshold)  # TODO: Leider muss ich den factor invertieren, da die LED die falsche Farbe angezeigt hat. Die GPIO Pins sind richtig verdrahtet, daher schließe ich daraus, dass es um eine raspberry pi konfiguration handeln müsste.

        r = factor
        g = 1 - factor
        b = 0

        logger.info(f"r: {r}, g: {g}, b: {b}, factor: {factor}")

        return (r, g, b)
