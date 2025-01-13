import threading
import logging
from abc import ABC, abstractmethod

class ThreadedService(ABC):
    def __init__(self, service_name, debug=False):
        self.service_name = service_name
        self._stop_event = threading.Event()
        self._thread = None
        self._is_running = False
        self.debug = debug
        self._logger = logging.getLogger(service_name)
        self._logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self._logger.info(f"{service_name} initialized")

    @abstractmethod
    def setup(self):
        """
        Perform setup tasks specific to the service.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def loop(self):
        """
        Main loop for the service. Executed in a separate thread.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Cleanup resources when stopping the service.
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
            try:
                self._thread.join(timeout=5)
                if self._thread.is_alive():
                    self._logger.warning(f"Thread for {self.service_name} did not finished in time")
            except KeyboardInterrupt:
                self._logger.warning(f"Interrupted while waiting for {self.service_name} to stop")
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
