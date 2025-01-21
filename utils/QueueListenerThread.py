from utils.ThreadedService import ThreadedService
from sensors.BaseSensor import BaseSensor
from outputs.BaseOutput import BaseOutput
from queue import Queue

class QueueListenerThread(ThreadedService):
    def __init__(self, service: BaseSensor | BaseOutput, target_output: Queue, debug=False):
        super().__init__(service.service_name, debug)
        self.target_output = target_output
        self.service = service

    def setup(self):
         self._logger.info(f"QueueListenerThread for {self.service.service_name} initialized")

    def loop(self):
        try:
            message = self.service.receive_message(queue= self.service.outgoing_queue, block=True, timeout=None)
            if message:
                self._logger.debug(f"Received message from {message.service}: {message.data}")
                self.service.send_message(
                    service_name=self.service.service_name,
                    data=message.data,
                    queue=self.target_output
                )
        except Exception as e:
            self._logger.error(f"Error in QueueListenerThread: {e}")

    def cleanup(self):
        super().cleanup()
        self._logger.info(f"QueueListenerThread for {self.service.service_name} stopped")

