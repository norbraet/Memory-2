import logging
from outputs.BaseOutput import BaseOutput
from dataclass.LedConfig import LedConfig
from gpiozero import PWMLED

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

    def loop(self):
        """
        Process the incoming queue.
        """

        self._set_color(r = 1, g = 1, b = 1)

        message = self.receive_message(queue=self.incoming_queue, block=True, timeout=None)
        data = message.data
        
        if isinstance(data, dict):
            if data.get("red") and data.get("green") and data.get("blue"): 
                self._set_color(r = data["red"], g = data["green"], b = data["blue"])


    def trigger_action(self, data):
        pass
    
    def cleanup(self):
        """Clean up the led resources properly before shutdown."""

        logger.info(f"Cleaning up {self.service_name}")

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