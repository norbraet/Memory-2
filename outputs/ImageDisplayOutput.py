import cv2
import queue
import time
import pygame
import numpy as np
from outputs.BaseOutput import BaseOutput
from enum import Enum, auto

class Stage(Enum):
    BLACK_WHITE = auto()
    BLURRY = auto()
    LIGHTNESS = auto()

class ImageDisplayOutput(BaseOutput):
    def __init__(self, service_name, message_queue = None, config = None, debug = False, image_path = "./assets/images/image.png"):
        """
        A sensor-like class for displaying images, extending BaseOutput.
        :param service_name: Unique name for the service.
        :param message_queue: Shared queue for communication.
        :param config: Optional configuration dictionary.
        :param debug: Enable debugging logs.
        :param image_path: Path to the initial image.
        """
        super().__init__(service_name, message_queue, config, debug)
        self.window_name = "Image Display"
        self.image_path = image_path
        self.original_image = None
        self.current_image = None

        self.stage = Stage.BLACK_WHITE
        self.level = 0
        self.reverse = False
    
    def setup(self):
        """
        Perform setup tasks, like loading the initial image and setting up the display window.
        """
        self._logger.info("Setting up ImageDisplayOutput")
        
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # You can adjust the size as needed
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(self.window_name)
        
        self.current_image = cv2.imread(self.image_path)

        if self.current_image is None:
            self._logger.error(f"Failed to load image from path: {self.image_path}")
        else:
            self._logger.info("Initial image loaded successfully.")
            self.original_image = self.current_image.copy()

    def loop(self):
        while not self._stop_event.is_set():
            self.current_image = self.degrade_image()
            try:
                self.message_queue.put_nowait(self.current_image)
            except queue.Full:
                self._logger.warning("Queue is full, skipping frame")
            time.sleep(1)

    def trigger_action(self, data = None):
        """Display images in a loop. This function works only in the main thread due to the restriction of cv2"""
        while not self._stop_event.is_set():
            if not self.message_queue.empty():
                current_image = self.message_queue.get()
                image_rgb = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
                image_rgb = np.transpose(image_rgb, (1, 0, 2))  # Swap width and height dimensions
                pygame_image = pygame.surfarray.make_surface(image_rgb)
                self.screen.blit(pygame_image, (0, 0))
                pygame.display.update()

    def cleanup(self):
        """
        Clean up resources, like destroying the display window.
        """
        self._logger.info("Cleaning up ImageDisplayOutput")
        pygame.quit()
    
    def _apply_black_white(self, image, level):
        """
        Gradually convert the image to black and white, or restore color.
        :param image: The original image.
        :param level: Percentage of black and white to apply (0-100%).
        """
        hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls_image)
        level = max(0, min(level, 100))
        scale_factor = (100 - level) / 100.0
        
        s = cv2.multiply(s, scale_factor)
        s = cv2.min(s, 255).astype(np.uint8)
        
        hls_image = cv2.merge([h, l, s])
        
        self._logger.debug(f"Applied black & white filter with level {level}% saturation reduction")
        
        return cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)

    def _apply_blur(self, image, level):
        """
        Gradually apply a subtle blur filter, or restore sharpness.
        :param image: The image to blur.
        :param level: The current blur level (0 to 10).
        """
        max_kernel_size = 11
        level = max(0, min(level, 100))
        scaled_level = int((level / 100) * (max_kernel_size - 3))
        kernel_size = 3 + scaled_level

        if kernel_size % 2 == 0:
            kernel_size += 1
        
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    def _apply_darkness(self, image, level):
        """
        Gradually apply brightness change, or reduce brightness.
        :param image: The image to adjust brightness.
        :param level: The current brightness level (0 to 10).
        """
        hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls_image)
        level = max(0, min(level, 100))
        scale_factor = (100 - level) / 100.0
        
        l = cv2.multiply(l, scale_factor)
        l = cv2.min(l, 255).astype(np.uint8)
        
        hls_image = cv2.merge([h, l, s])
        self._logger.debug(f"Applied darkness filter with level {level}%")
        
        return cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)
    
    def degrade_image(self):
        match self.stage:
            case Stage.BLACK_WHITE:
                if self.level < 100:
                    self.level += 5
                    return self._apply_black_white(self.current_image, self.level)
                else:
                    self.stage = Stage.BLURRY
                    self.level = 0
                    return self.current_image
            case Stage.BLURRY:
                if self.level < 100:
                    self.level += 5
                    return self._apply_blur(self.current_image, self.level)
                else:
                    self.stage = Stage.LIGHTNESS
                    self.level = 0
                    return self.current_image
            case Stage.LIGHTNESS:
                if self.level < 100:
                    self.level += 5
                    return self._apply_darkness(self.current_image, self.level)
                else:
                    return self.current_image

    def restore_image(self):
        """
        Gradually restore the image step by step.
        """
        # TODO: Needs to be implemented
        pass
