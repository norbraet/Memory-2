from enums.ServicesEnum import ServicesEnum
from outputs.BaseOutput import BaseOutput
from outputs.ImageDisplayOutput import ImageDisplayOutput
from outputs.VibrationMotorOutput import VibrationMotorOutput
from sensors.BaseSensor import BaseSensor
from sensors.FaceRecognition import FaceRecognition
from sensors.TouchSensor import TouchSensor
from sensors.UltrasonicSensor import UltrasonicSensor
from utils.QueueListenerThread import QueueListenerThread
from queue import Queue
import logging

class OutputController():
    def __init__(self, config = None, debug = False):
        self.config = config or {}
        self.debug = debug
        self._logger = self._intialize_logger()
        self.sensors = None
        self.outputs = None
        self.queue_threads = []

    def _intialize_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        return logger
    
    def start(self):
        self._setup()
        self._start_services_and_outputs()
        self._start_queue_threads()
        self._start_gui()
        self._logger.info("All services started")

    def stop(self):
        self._stop_queue_threads()
        self._stop_services_and_outputs()

    def _start_gui(self):
        self.outputs[ServicesEnum.ImageDisplayOutput].trigger_action()

    def _setup(self):
        self.outputs: dict[ServicesEnum, BaseOutput] = {
            ServicesEnum.ImageDisplayOutput: ImageDisplayOutput(service_name = ServicesEnum.ImageDisplayOutput.value, debug = False),
            ServicesEnum.VibrationMotorOutput: VibrationMotorOutput(service_name=ServicesEnum.VibrationMotorOutput.value, debug = True)
        }
        self.sensors: dict[ServicesEnum, BaseSensor] = {
            ServicesEnum.FaceRecognition: FaceRecognition(service_name = ServicesEnum.FaceRecognition.value, debug = False),
            ServicesEnum.UltrasonicSensor: UltrasonicSensor(service_name = ServicesEnum.UltrasonicSensor.value, debug = False),
            ServicesEnum.TouchSensor: TouchSensor(service_name = ServicesEnum.TouchSensor.value, debug = False),
        }

        self.output_incoming_queues: dict[ServicesEnum, Queue] = {
            service_enum: output.incoming_queue 
            for service_enum, output in self.outputs.items()
        }
        
    def _start_services_and_outputs(self):
        """
        Initialize and start all sensors and outputs.
        """
        for sensor in self.sensors.values():
            sensor.start()
        
        for output in self.outputs.values():
            output.start()

    def _start_queue_threads(self):
        for sensor in self.sensors.values():
            queue_thread = QueueListenerThread(
                service=sensor,
                target_output=self.output_incoming_queues,
                debug=sensor.debug
            )
            self.queue_threads.append(queue_thread)
            queue_thread.start()

    def _stop_services_and_outputs(self):
        """
        Stop and clean up all services.
        """
        for sensor in self.sensors.values():
            try:
                sensor.stop()
            except KeyboardInterrupt:
                self._logger.warning(f"Interrupted while stopping {sensor.service_name}")

        for output in self.outputs.values():
            try:
                output.stop()
            except KeyboardInterrupt:
                self._logger.warning(f"Interrupted while stopping {output.service_name}")
    
    def _stop_queue_threads(self):
        for thread in self.queue_threads:
            thread.stop()
