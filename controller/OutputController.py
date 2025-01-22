from enums.ServicesEnum import ServicesEnum
from outputs.ImageDisplayOutput import ImageDisplayOutput
from sensors.FaceRecognition import FaceRecognition
from sensors.TouchSensor import TouchSensor
from sensors.UltrasonicSensor import UltrasonicSensor
from utils.QueueListenerThread import QueueListenerThread
from utils.MessagingService import MessagingService

import logging

class OutputController():
    def __init__(self, service_name, config = None, debug = False):
        self.service_name = service_name
        self.config = config or {}
        self.debug = debug
        self._logger = self._intialize_logger()
        self.services = None
        self.queue_threads = []

    def _intialize_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        return logger
    
    def start(self):
        self._setup()
        self._start_services()
        self._start_queue_threads()
        self._start_gui()
        self._logger.info("All services started")

    def stop(self):
        self._stop_queue_threads()
        self._stop_services()

    def _start_gui(self):
        self.services[ServicesEnum.ImageDisplayOutput].trigger_action()

    def _setup(self):
        self.services = {
            # ServicesEnum.FaceRecognition: FaceRecognition(service_name = ServicesEnum.FaceRecognition.value, debug = False),
            ServicesEnum.UltrasonicSensor: UltrasonicSensor(service_name = ServicesEnum.UltrasonicSensor.value, debug = False),
            # ServicesEnum.TouchSensor: TouchSensor(service_name = ServicesEnum.TouchSensor.value, debug = False),
            ServicesEnum.ImageDisplayOutput: ImageDisplayOutput(service_name = ServicesEnum.ImageDisplayOutput.value, debug = False)
        }
        
    def _start_services(self):
        """
        Initialize and start all services.
        """
        for service in self.services.values():
            service.start()#
    
    def _start_queue_threads(self):
        for service in self.services.values():
            queue_thread = QueueListenerThread(
                service=service,
                target_output=self.services[ServicesEnum.ImageDisplayOutput].incoming_queue,
                debug=self.debug
            )
            self.queue_threads.append(queue_thread)
            queue_thread.start()

    def _stop_services(self):
        """
        Stop and clean up all services.
        """
        for service in self.services.values():
            try:
                service.stop()
            except KeyboardInterrupt:
                self._logger.warning(f"Interrupted while stopping {service.service_name}")
    
    def _stop_queue_threads(self):
        for thread in self.queue_threads:
            thread.stop()
