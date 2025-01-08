import threading
import logging
from abc import ABC, abstractmethod
from queue import Queue, Empty
from dataclass.Message import Message

class BaseSensor(ABC):
    def __init__(self, service_name, message_queue=None, config=None):
        """
        Base class for all services.
        :param service_name: Unique name for the service (e.g., "FaceRecognitionService").
        :param message_queue: Shared queue for inter-service or main communication.
        :param config: Optional configuration dictionary for service-specific parameters.
        """
        self.service_name = service_name
        self.message_queue = message_queue
        self.config = config or {}

        self._stop_event = threading.Event()
        self._thread = None
        self._is_running = False
        self._logger = logging.getLogger(service_name)
        self._logger.setLevel(logging.INFO)
        self._logger.info(f"{service_name} initialized")

    @abstractmethod
    def setup(self):
        """
        Perform setup tasks specific to the service (e.g., initializing hardware, loading models).
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def loop(self):
        """
        The main loop for the service. This is executed in a separate thread.
        Must be implemented by subclasses.
        """
        pass

    def start(self):
        """
        Start the service and its background thread.
        """
        self.setup()
        self._is_running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._logger.info(f"Starting {self.service_name}")

    def stop(self):
        """
        Stop the service and clean up resources.
        """
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.cleanup()
        self._is_running = False
        self._logger.info(f"Stopping {self.service_name}")

    def _run(self):
        """
        Internal method to run the loop in a thread.
        """
        self._logger.info(f"{self.service_name} is running")
        while not self._stop_event.is_set():
            try:
                self.loop()
            except Exception as e:
                self._logger.error(f"Error in {self.service_name}: {e}")

    @abstractmethod
    def cleanup(self):
        """
        Perform cleanup tasks (e.g., releasing hardware, saving state).
        Must be implemented by subclasses.
        """
        pass

    def send_message(self, data, metadata = None):
        """
        Send a message to the main application or other services via the queue.
        """
        if self.message_queue:

            message = Message(
                service = self.service_name,
                data = data,
                metadata = metadata
            )

            self.message_queue.put(message)

    def receive_message(self, timeout=1):
        """
        Receive a message from the queue, if available.
        """
        try:
            return self.message_queue.get(timeout=timeout)
        except Empty:
            return None
