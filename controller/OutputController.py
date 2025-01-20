from utils.MessagingService import MessagingService
from utils.ThreadedService import ThreadedService
from dataclass.ServicesEnum import ServicesEnum
from outputs.ImageDisplayOutput import ImageDisplayOutput
from sensors.FaceRecognition import FaceRecognition
from sensors.TouchSensor import TouchSensor
from sensors.UltrasonicSensor import UltrasonicSensor

import time

class OutputController(ThreadedService, MessagingService):
    def __init__(self, service_name, config = None, debug = False):
        ThreadedService.__init__(self, service_name, debug)
        MessagingService.__init__(self)
        self.config = config or {}
        self.services = None

    def setup(self):
        self.services = {
            # Services.FaceRecognition: FaceRecognition(service_name = Services.FaceRecognition.value, message_queue = sensor_message_queue, debug = False),
            # Services.UltrasonicSensor: UltrasonicSensor(service_name = Services.UltrasonicSensor.value, message_queue = sensor_message_queue, debug = False),
            # Services.TouchSensor: TouchSensor(service_name = Services.TouchSensor.value, message_queue = touch_message_queue, debug = False),
            ServicesEnum.ImageDisplayOutput: ImageDisplayOutput(service_name = ServicesEnum.ImageDisplayOutput.value)
        }
        self._initialize_services(self.services.values())
        self._logger.info("All services started")


    def loop(self):
        time.sleep(20)
        self.services[ServicesEnum.ImageDisplayOutput].send_message(
            service_name = self.services[ServicesEnum.ImageDisplayOutput].service_name,
            data = {
                "time": 10,
                "strength": 10
            },
            queue = self.services[ServicesEnum.ImageDisplayOutput].incoming_queue
        )
        time.sleep(5)
        print("Füge jetzt extra hinzu")
        self.services[ServicesEnum.ImageDisplayOutput].send_message(
            service_name = self.services[ServicesEnum.ImageDisplayOutput].service_name,
            data = {
                "time": 5,
                "strength": 5
            },
            queue = self.services[ServicesEnum.ImageDisplayOutput].incoming_queue
        )

    def cleanup(self):
        self._stop_services(self.services.values())

    def start_gui(self):
        self.services[ServicesEnum.ImageDisplayOutput].trigger_action()

    def _initialize_services(self, services):
        """
        Initialize and start all services in the provided list.
        """
        for service in services:
            service.start()

    def _stop_services(self, services):
        """
        Stop and clean up all services in the provided list.
        """
        for service in services:
            try:
                service.stop()
            except KeyboardInterrupt:
                self._logger.warning(f"Interrupted while stopping {service.service_name}")

