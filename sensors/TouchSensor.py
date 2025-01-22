import logging
import time
from evdev import InputDevice, ecodes, list_devices
from sensors.BaseSensor import BaseSensor
from dataclass.TouchConfig import TouchConfig

logger = logging.getLogger(__name__)

class TouchSensor(BaseSensor):
    def __init__(self, service_name, device_name="QDTECH̐MPI700 MPI7002", config=None, debug=False):
        """
        A sensor for handling touch input events.

        :param service_name: Name of the service.
        :param device_name: Name of the touch input device.
        :param config: Optional configuration parameters.
        :param debug: Enables debug mode for detailed logging.
        """
        super().__init__(service_name, config, debug)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.device_name = device_name
        self.device_path = None
        self.touch_device = None
        self.debug = debug
        self.config: TouchConfig = config or TouchConfig()

    def setup(self):
        """
        Set up the touch sensor by finding and initializing the input device.
        """
        try:
            devices = [InputDevice(path) for path in list_devices()]
            for device in devices:
                if device.name == self.device_name:
                    self.device_path = device.path
                    break
            
            if self.device_path:
                self.touch_device = InputDevice(self.device_path)
                logger.info(f"Touch device initialized: {self.touch_device.name} at {self.device_path}")
            else:
                raise FileNotFoundError(f"Device with name '{self.device_name}' not found.")
        
        except FileNotFoundError as e:
            logger.error(e)
            self.stop()
        except Exception as e:
            logger.error(f"Unexpected error during setup: {e}")
            self.stop()

    def loop(self):
        """
        Main loop to read and handle touch events.
        """
        if not self.touch_device:
            logger.error("Touch device not initialized")
            self.stop()
            return
        
        try:
            for event in self.touch_device.read_loop():
                if event.type == ecodes.EV_ABS:
                    """ self.send_message(
                        service_name = self.service_name,
                        data = {
                            "amount": 0.01,
                        },
                        queue=self.outgoing_queue,
                        metadata = {
                            "type": "swipe"
                        }
                    ) """

                    """ 
                    TODO: Die idee ist das wir nicht jeden einzelnen swipe als event schicken sondern nur zwei: einmal "Touch down" und "Touch Up". Beim
                    Touch Down soll sich der Overlay anfangen abzubauen und sobald Touch Up kommt wird dieser Prozess angehalten
                    """
                        
                    if event.code == ecodes.ABS_X:
                        #logger.debug(f"X Position: {event.value}")
                        # TODO: Hier muss eine Message gesendet werden, die dazu dient die overlay opacity zu regulieren
                        pass
                    elif event.code == ecodes.ABS_Y:
                        # logger.debug(f"Y Position: {event.value}")
                        # TODO: Hier muss eine Message gesendet werden, die dazu dient die overlay opacity zu regulieren
                        pass
                        
                elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                    if event.value == 1:
                        logger.debug("Touch down")
                        self.send_message(service_name = self.service_name,
                                        data = {
                                            "time": self.config.restoration_duration,
                                            "level_steps": self.config.level_steps
                                        },
                                        queue=self.outgoing_queue)
                        
                    elif event.value == 0:
                        # logger.debug("Touch up")
                        pass
                         
        except Exception as e:
            logger.error(f"Error in touch sensor loop: {e}")
            self.stop()

    def cleanup(self):
        """
        Clean up the touch sensor by releasing resources.
        """
        if self.touch_device:
            logger.info(f"Closing touch device: {self.touch_device.name}")
            self.touch_device.close()
            self.touch_device = None