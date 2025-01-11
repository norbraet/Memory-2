import cv2
from outputs.BaseOutput import BaseOutput

class ImageDisplayOutput(BaseOutput):
    def __init__(self, service_name, config=None, debug=False):
        super().__init__(service_name, config, debug)
        self.window_name = "Image Display"
        self.default_color = (0, 0, 0)
        self.current_image = None

    def setup(self):
        self._logger.info("Setting up ImageDisplayOutput")
        cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        self.current_image = self._create_default_image()