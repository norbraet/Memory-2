from enums.ServicesEnum import ServicesEnum
from outputs.BaseOutput import BaseOutput
from outputs.ImageDisplayOutput import ImageDisplayOutput
from outputs.VibrationMotorOutput import VibrationMotorOutput
from outputs.LedOutput import LedOutput
from sensors.BaseSensor import BaseSensor
from sensors.FaceRecognition import FaceRecognition
from sensors.TouchSensor import TouchSensor
from sensors.UltrasonicSensor import UltrasonicSensor
from utils.QueueListenerThread import QueueListenerThread
from dataclass.FaceRecognitionConfig import FaceRecognitionConfig
from dataclass.UltrasonicConfig import UltrasonicConfig

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
        self.output_incoming_queues = None
        self.all_services = None

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
        
        # self._setup_normal()
        # self._setup_open()
        self._setup_reservedly()

        self.output_incoming_queues: dict[ServicesEnum, Queue] = {
            service_enum: output.incoming_queue 
            for service_enum, output in self.outputs.items()
        }

        self.all_services = list(self.sensors.values()) + list(self.outputs.values())
        
    def _start_services_and_outputs(self):
        """
        Initialize and start all sensors and outputs.
        """
        for service in self.all_services:
            service.start()
        

    def _start_queue_threads(self):
        for service in self.all_services:
            queue_thread = QueueListenerThread(
                service=service,
                output_queues=self.output_incoming_queues,
                debug=service.debug
            )
            self.queue_threads.append(queue_thread)
            queue_thread.start()

    def _stop_services_and_outputs(self):
        """
        Stop and clean up all services.
        """
        for service in self.all_services:
            try:
                service.stop()
            except KeyboardInterrupt:
                self._logger.warning(f"Interrupted while stopping {service.service_name}")
    
    def _stop_queue_threads(self):
        for thread in self.queue_threads:
            thread.stop()

    def _setup_normal(self):
        self.outputs: dict[ServicesEnum, BaseOutput] = {
            ServicesEnum.ImageDisplayOutput: ImageDisplayOutput(service_name = ServicesEnum.ImageDisplayOutput.value, debug = True),
            ServicesEnum.VibrationMotorOutput: VibrationMotorOutput(service_name=ServicesEnum.VibrationMotorOutput.value, debug = True),
            ServicesEnum.LedOutput: LedOutput(service_name=ServicesEnum.LedOutput.value, debug = True )
        }
        self.sensors: dict[ServicesEnum, BaseSensor] = {
            ServicesEnum.FaceRecognition: FaceRecognition(service_name = ServicesEnum.FaceRecognition.value, debug = True),
            ServicesEnum.UltrasonicSensor: UltrasonicSensor(service_name = ServicesEnum.UltrasonicSensor.value, debug = True),
            ServicesEnum.TouchSensor: TouchSensor(service_name = ServicesEnum.TouchSensor.value, debug = True),
        } 

    def _setup_open(self):
        faceRecognitionConfig = FaceRecognitionConfig(
            level_steps = 100,
            level_steps_max = 100,
            level_steps_min = 80,
            level_steps_interval = 10,
            restoration_duration = 20,
            restoration_duration_max = 30,
            restoration_duration_min = 10,
            restoration_duration_interval = 5
        )
        ultrasonicSensorConfig = UltrasonicConfig(
            level_steps = 80,
            level_steps_max = 100,
            level_steps_min = 50,
            level_steps_interval = 10,
            restoration_duration = 5,
            restoration_duration_max = 10,
            restoration_duration_min = 1,
            restoration_duration_interval = 1,
            threshold = 300
        )
        self.outputs: dict[ServicesEnum, BaseOutput] = {
            ServicesEnum.ImageDisplayOutput: ImageDisplayOutput(service_name = ServicesEnum.ImageDisplayOutput.value, debug = True),
            ServicesEnum.VibrationMotorOutput: VibrationMotorOutput(service_name=ServicesEnum.VibrationMotorOutput.value, debug = True),
            ServicesEnum.LedOutput: LedOutput(service_name=ServicesEnum.LedOutput.value, debug = True )
        }
        self.sensors: dict[ServicesEnum, BaseSensor] = {
            ServicesEnum.FaceRecognition: FaceRecognition(service_name = ServicesEnum.FaceRecognition.value, debug = True, config=faceRecognitionConfig),
            ServicesEnum.UltrasonicSensor: UltrasonicSensor(service_name = ServicesEnum.UltrasonicSensor.value, debug = True, config = ultrasonicSensorConfig),
            ServicesEnum.TouchSensor: TouchSensor(service_name = ServicesEnum.TouchSensor.value, debug = True),
        }

    def _setup_reservedly(self):
        faceRecognitionConfig = FaceRecognitionConfig(
            level_steps = 10,
            level_steps_max = 100,
            level_steps_min = 0,
            level_steps_interval = 4,
            restoration_duration = 4,
            restoration_duration_max = 10,
            restoration_duration_min = 1,
            restoration_duration_interval = 1
        )
        ultrasonicSensorConfig = UltrasonicConfig(
            level_steps = 0.1,
            level_steps_max = 1,
            level_steps_min = 0.1,
            level_steps_interval = 0.1,
            restoration_duration = 0.5,
            restoration_duration_max = 1,
            restoration_duration_min = 0.1,
            restoration_duration_interval = 0.1,
            threshold = 50
        )
        self.outputs: dict[ServicesEnum, BaseOutput] = {
            ServicesEnum.ImageDisplayOutput: ImageDisplayOutput(service_name = ServicesEnum.ImageDisplayOutput.value, debug = True, level_steps=10),
            ServicesEnum.VibrationMotorOutput: VibrationMotorOutput(service_name=ServicesEnum.VibrationMotorOutput.value, debug = True),
            ServicesEnum.LedOutput: LedOutput(service_name=ServicesEnum.LedOutput.value, debug = True )
        }
        self.sensors: dict[ServicesEnum, BaseSensor] = {
            ServicesEnum.FaceRecognition: FaceRecognition(service_name = ServicesEnum.FaceRecognition.value, debug = True, config=faceRecognitionConfig),
            ServicesEnum.UltrasonicSensor: UltrasonicSensor(service_name = ServicesEnum.UltrasonicSensor.value, debug = True, config = ultrasonicSensorConfig),
            ServicesEnum.TouchSensor: TouchSensor(service_name = ServicesEnum.TouchSensor.value, debug = True),
        }