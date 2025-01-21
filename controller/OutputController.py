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
            # ServicesEnum.FaceRecognition: FaceRecognition(service_name = ServicesEnum.FaceRecognition.value, debug = False),
            ServicesEnum.UltrasonicSensor: UltrasonicSensor(service_name = ServicesEnum.UltrasonicSensor.value, debug = False),
            # ServicesEnum.TouchSensor: TouchSensor(service_name = ServicesEnum.TouchSensor.value, debug = False),
            ServicesEnum.ImageDisplayOutput: ImageDisplayOutput(service_name = ServicesEnum.ImageDisplayOutput.value, debug = False)
        }
        self._initialize_services(self.services.values())
        self._logger.info("All services started")


    def loop(self):
        """
        Continuously check the outgoing queues of all services and delegate messages to the ImageDisplayOutput.
        """

        
        """
        Idee: Jede Service-Queue bekommt einen eigenen Thread damit die Performance besser ist. In diesem Thread wird mit einem blockierendem aufruf auf die Queue gewartet bis was reinkommt. 
        
        """
        message = self.services[ServicesEnum.UltrasonicSensor].receive_message(queue=self.services[ServicesEnum.UltrasonicSensor].outgoing_queue, timeout = None).data
        self._logger.info(f"Received message: {message}")
        self.services[ServicesEnum.ImageDisplayOutput].send_message(
            service_name = self.services[ServicesEnum.ImageDisplayOutput].service_name,
            data = message,
            queue = self.services[ServicesEnum.ImageDisplayOutput].incoming_queue
        )



        """ for service_enum, service in self.services.items():
            if hasattr(service, "outgoing_queue") and not service.outgoing_queue.empty():
                message = service.receive_message(queue=service.outgoing_queue).data
                self._logger.info(f"Received message from {service_enum}: {message}")
                self.services[ServicesEnum.ImageDisplayOutput].send_message(
                    service_name = self.services[ServicesEnum.ImageDisplayOutput].service_name,
                    data = message,
                    queue = self.services[ServicesEnum.ImageDisplayOutput].incoming_queue
                )
            time.sleep(0.1) """

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

