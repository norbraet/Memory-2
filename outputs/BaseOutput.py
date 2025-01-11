import logging
from abc import ABC, abstractmethod

class BaseOutput(ABC):
    def __init__(self, service_name, config=None, debug=False):
        """
        Base class for all output devices.
        :param service_name: Unique name for the service (e.g., "ImageDisplayOutput").
        :param config: Optional configuration dictionary for device-specific parameters.
        :param debug: Enables debug mode for verbose logging.
        """
        self.service_name = service_name
        self.config = config or {}
        self.debug = debug
        self._logger = logging.getLogger(service_name)
        self._logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self._logger.info(f"{service_name} initialized")

    @abstractmethod
    def setup(self):
        """
        Perform setup tasks specific to the output device (e.g., initializing hardware).
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def trigger_action(self, data):
        """
        Perform the output action (e.g., display an image, blink an LED, vibrate).
        Must be implemented by subclasses.
        :param data: The data or command triggering the action.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Perform cleanup tasks (e.g., releasing hardware resources).
        Must be implemented by subclasses.
        """
        pass

