import logging
from outputs.BaseOutput import BaseOutput
from dataclass.VibrationMotorConfig import VibrationMotorConfig
from gpiozero import PWMOutputDevice
from time import sleep

logger = logging.getLogger(__name__)

class VibrationMotorOutput(BaseOutput):
    def __init__(self, service_name, config:VibrationMotorConfig=None, debug=False):
        config = config or VibrationMotorConfig()
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        super().__init__(service_name, config, debug)
        self.config = config
        self.motor = None

    def setup(self):
        logger.info("Setting up vibration motor.")
        self.motor = PWMOutputDevice(self.config.in_pin)

    def loop(self):
        """
        Process the incoming queue.
        """
        message = self.receive_message(queue=self.incoming_queue, block=True, timeout=None)
        data = message.data
        
        if isinstance(data, dict):
            if data.get("time") and data.get("pwm"): 
                self.motor.value = data["pwm"]
                sleep(data["time"])
                self.motor.value = 0


    def trigger_action(self, data):
        pass
    
    def cleanup(self):
        """Clean up the motor resources properly before shutdown."""

        logger.info(f"Cleaning up {self.service_name}")

        if self.motor:
            self.motor.value = 0
            self.motor.close()
            logger.info("Motor has been turned off and cleaned up.")