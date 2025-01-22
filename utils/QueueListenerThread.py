import logging
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
            """
            TODO: Aktuell haben wir mit timeout=None eine unendlich lange Wartezeit. Man könnte sagen, nach dem Zeit x vergangen ist, dass der Sensor bockig wird und die Werte der 
            config ändert. da die Config eine @dataclass sind, können die Werte im Nachhinein geändert werden. Auf der anderen Seite wenn viel Interaktion mit einem Sensor passiert, so kann
            der Wert auch sich steigern. Dazu müsste ich bei jeder Interaktion den Wert erhöhen.
            """
            
            message = self.service.receive_message(queue= self.service.outgoing_queue, block=True, timeout=10)
            if message:
                logger.debug(f"Received message from {message.service}: {message.data}")
                self.service.send_message(
                    service_name=self.service.service_name,
                    data=message.data,
                    queue=self.target_output
                )
                if self.config.level_steps < self.config.level_steps_max:
                    logger.debug(f"I will increase restoration strength ({self.config.level_steps}) by {self.config.level_steps_interval}")
                    self.config.level_steps += self.config.level_steps_interval

                if self.config.restoration_duration < self.config.restoration_duration_max:
                    logger.debug(f"I will increase restoration time ({self.config.restoration_duration}) by {self.config.restoration_duration_interval}")
                    self.config.restoration_duration += self.config.restoration_duration_interval

        except Empty:
            logger.debug(f"No message received within timeout.")
    
            if self.config.level_steps > self.config.level_steps_min:
                logger.debug(f"I will decrease strength ({self.config.level_steps}) by {self.config.level_steps_interval}")
                self.config.level_steps -= self.config.level_steps_interval
            
            if self.config.restoration_duration > self.config.restoration_duration_max:
                logger.debug(f"I will decrease restoration time ({self.config.restoration_duration}) by {self.config.restoration_duration_interval}")
                self.config.restoration_duration -= self.config.restoration_duration_interval

        except Exception as e:
            logger.error(f"Error in QueueListenerThread: {e}")

    def cleanup(self):
        super().cleanup()
        logger.info(f"QueueListenerThread for {self.service.service_name} stopped")

