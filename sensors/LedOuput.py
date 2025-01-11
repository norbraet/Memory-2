import threading 
import logging 


from gpiozero import PWMOutputDevice
from dataclass import LedData
from time import sleep
from outputs.BaseOutput import BaseOutput
from dataclass import LedOutputConfig


class LedOutput(BaseOutput): 
    def __init__(self, 
                service_name = "LedOutput",
                debug = False, 
                config: LedOutputConfig = None): 
        config = config or LedOutputConfig()
        super().__init__(service_name, config, debug)

        self.red = PWMOutputDevice(17)      # Red pin connected to GPIO 17
        self.green = PWMOutputDevice(27)    # Green pin connected to GPIO 27
        self.blue = PWMOutputDevice(22)     # Blue pin connected to GPIO 22
        
    def setup(self): 
        if self.debug: 
            self._logger.info("Time to debug")


    def trigger_action(self, data: LedData):
        self.red.value = data.r  # Set the brightness for Red
        self.green.value = data.g  # Set the brightness for Green
        self.blue.value = data.b  # Set the brightness for Blue