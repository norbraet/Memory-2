import logging
import time
from utils.ThreadedService import ThreadedService
from sensors.BaseSensor import BaseSensor
from outputs.BaseOutput import BaseOutput
from queue import Empty, Queue
from dataclass.BaseConfig import BaseConfig

logger = logging.getLogger(__name__)

class QueueListenerThread(ThreadedService):
    def __init__(self, service: BaseSensor | BaseOutput, target_output: Queue, debug=False):
        super().__init__(service.service_name, debug)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.target_output = target_output
        self.service = service
        self.config: BaseConfig = service.config

    def setup(self):
         logger.info(f"QueueListenerThread for {self.service.service_name} initialized")

    def loop(self):
        try:
            message = self.service.receive_message(queue= self.service.outgoing_queue, block=True, timeout=30)
            if message:
                logger.debug(f"Received message from {message.service}: {message.data}")
                self.service.send_message(
                    service_name=self.service.service_name,
                    data=message.data,
                    queue=self.target_output
                )
                if self.config.level_steps < self.config.level_steps_max:
                    logger.debug(f"{self.service.service_name} | I will increase restoration strength ({self.config.level_steps}) by {self.config.level_steps_interval}")
                    self.config.level_steps += self.config.level_steps_interval

                if self.config.restoration_duration < self.config.restoration_duration_max:
                    logger.debug(f"{self.service.service_name} | I will increase restoration time ({self.config.restoration_duration}) by {self.config.restoration_duration_interval}")
                    self.config.restoration_duration += self.config.restoration_duration_interval
                time.sleep(self.config.restoration_duration * 0.9)

        except Empty:
            logger.debug(f"No message received within timeout.")
    
            if self.config.level_steps > self.config.level_steps_min:
                logger.debug(f"{self.service.service_name} | I will decrease strength ({self.config.level_steps}) by {self.config.level_steps_interval}")
                self.config.level_steps -= self.config.level_steps_interval
            
            if self.config.restoration_duration > self.config.restoration_duration_min:
                logger.debug(f"{self.service.service_name} | I will decrease restoration time ({self.config.restoration_duration}) by {self.config.restoration_duration_interval}")
                self.config.restoration_duration -= self.config.restoration_duration_interval

        except Exception as e:
            logger.error(f"Error in QueueListenerThread: {e}")

    def cleanup(self):
        super().cleanup()
        logger.info(f"QueueListenerThread for {self.service.service_name} stopped")

