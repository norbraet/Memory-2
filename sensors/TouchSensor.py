from evdev import InputDevice, ecodes
from sensors.BaseSensor import BaseSensor

class TouchSensor(BaseSensor):
    def __init__(self, service_name, device_path='/dev/input/event7', message_queue=None, config=None, debug=False):
        """
        A sensor for handling touch input events.

        :param service_name: Name of the service.
        :param device_path: Path to the touch input device (e.g., /dev/input/eventX).
        :param message_queue: Queue for inter-service communication.
        :param config: Optional configuration parameters.
        :param debug: Enables debug mode for detailed logging.
        """
        # TODO: MessagingService korrekt einbinden mit outgoing und incoming queues
        super().__init__(service_name, message_queue, config, debug)
        self.device_path = device_path
        self.touch_device = None

    def setup(self):
        """
        Set up the touch sensor by initializing the input device.
        """
        try:
            self.touch_device = InputDevice(self.device_path)
            self._logger.info(f"Touch device initialized: {self.touch_device.name}")
        except FileNotFoundError:
            self._logger.error(f"Device not found at {self.device_path}. Check your device path.")
            self.stop()

    def loop(self):
        """
        Main loop to read and handle touch events.
        """
        if not self.touch_device:
            self._logger.error("Touch device not initialized")
            self.stop()
            return
        
        try:
            for event in self.touch_device.read_loop():
                if event.type == ecodes.EV_ABS:
                    if event.code == ecodes.ABS_X:
                        self._logger.debug(f"X Position: {event.value}")
                        self.send_message(service_name = self.service_name,
                                          data = {"type": "position", "axis": "x", "value": event.value})
                    elif event.code == ecodes.ABS_Y:
                        self._logger.debug(f"Y Position: {event.value}")
                        self.send_message(service_name = self.service_name,
                                          data = {"type": "position", "axis": "y", "value": event.value})
                
                elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                    if event.value == 1:
                        self._logger.debug("Touch down")
                        self.send_message(service_name = self.service_name,
                                          data = {"type": "touch", "action": "down"}
                                          )
                    elif event.value == 0:
                        self._logger.debug("Touch up")
                        self.send_message(service_name = self.service_name,
                                          data = {"type": "touch", "action": "up"})
        except Exception as e:
            self._logger.error(f"Error in touch sensor loop: {e}")
            self.stop()

    def cleanup(self):
        """
        Clean up the touch sensor by releasing resources.
        """
        if self.touch_device:
            self._logger.info(f"Closing touch device: {self.touch_device.name}")
            self.touch_device.close()
            self.touch_device = None