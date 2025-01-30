import cv2
import time
import logging
import pygame
import numpy as np
from outputs.BaseOutput import BaseOutput
from enums.StageEnum import Stage
from enums.ServicesEnum import ServicesEnum

logger = logging.getLogger(__name__)

class ImageDisplayOutput(BaseOutput):
    LEVEL_LIMIT = 100

    def __init__(self, service_name, config = None, debug = False, image_path = "./assets/images/image.png", level_steps = 1, step_intervall_seconds = 0.1):
        """
        A sensor-like class for displaying images, extending BaseOutput.
        :param service_name: Unique name for the service.
        :param config: Optional configuration dictionary.
        :param debug: Enable debugging logs.
        :param image_path: Path to the initial image.
        :param level_steps: Step interval until the level limit is reached
        :param step_interval_seconds: Time interval between steps, in seconds.
        """
        self.config = config
        super().__init__(service_name, config, debug)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.window_name = self.service_name
        self.image_path = image_path
        self.original_image = None
        self.current_image = None

        self.stage = Stage.START
        self.level = 0
        self.level_steps = level_steps
        self.level_steps_init = level_steps
        self.reverse = False
        self.step_intervall_seconds = step_intervall_seconds
        self.difficulty = 2

        self.restoration = False
        self.restoration_duration = 0
        self.restoration_start_time:float = None

    
    def setup(self):
        """
        Perform setup tasks, like loading the initial image and setting up the display window.
        """
        logger.info("Setting up ImageDisplayOutput")
        
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(self.window_name)
        
        self.current_image = cv2.imread(self.image_path)

        if self.current_image is None:
            logger.error(f"Failed to load image from path: {self.image_path}")
        else:
            logger.debug("Initial image loaded successfully.")
            self.original_image = self.current_image.copy()

    def loop(self):  
        if not self.reverse:
            self.current_image = self._degrade_image()
            self.send_message(service_name = self.service_name, data = self.current_image, queue = self.internal_queue, block = False )
        else:
            self.current_image = self._restore_image()
            self.send_message(service_name = self.service_name, data = self.current_image, queue = self.internal_queue, block = False )
        
        time.sleep(self.step_intervall_seconds)

    def trigger_action(self, data = None):
        """
        Display images in a loop. This function works only in the main thread due to the restriction of pygame.
        """

        while not self._stop_event.is_set():
            self._process_incoming_queue()
            self.reverse = True if self._is_restoration_active() else self._reset_restoration() 
            self._process_internal_queue()

    def cleanup(self):
        """
        Clean up resources, like destroying the display window.
        """
        logger.info("Cleaning up ImageDisplayOutput")
        pygame.quit()

    def _display_image(self, image):
        """
        Utility function to display the current image using Pygame.
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb = np.transpose(image_rgb, (1, 0, 2))  # Swap width and height dimensions

        if image_rgb.shape[0] > 0 and image_rgb.shape[1] > 0:
            pygame_image = pygame.surfarray.make_surface(image_rgb)
            self.screen.blit(pygame_image, (0, 0))
            pygame.display.update()
        else:
            logger.error("Image dimensions are invalid for display.")

    
    def _apply_black_white(self, image, level):
        """
        Gradually convert the image to black and white, or restore color.
        :param image: The original image.
        :param level: Percentage of black and white to apply (0-100%).
        """
        """
        TODO: Schwar-Weiß Filter ist zu schnell
        """
        hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls_image)
        level = max(0, min(level, self.LEVEL_LIMIT))
        scale_factor = (self.LEVEL_LIMIT - level) / float(self.LEVEL_LIMIT)
        
        s = cv2.multiply(s, scale_factor)
        s = cv2.min(s, 255).astype(np.uint8)
        
        hls_image = cv2.merge([h, l, s])
        
        
        return cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)

    def _apply_blur(self, image, level):
        """
        Gradually apply a subtle blur filter, or restore sharpness.
        :param image: The image to blur.
        :param level: The current blur level (0 to 10).
        """
        max_kernel_size = 11
        level = max(0, min(level, self.LEVEL_LIMIT))
        scaled_level = int((level / self.LEVEL_LIMIT) * (max_kernel_size - 3))
        kernel_size = 3 + scaled_level

        if kernel_size % 2 == 0:
            kernel_size += 1


        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    def _apply_darkness(self, image, level):
        """
        Gradually apply brightness change, or reduce brightness.
        :param image: The image to adjust brightness.
        :param level: The current brightness level (0 to LEVEL_LIMIT).
        """
        """
        TODO: Helligkeits Filter ist zu schnell
        """
        
        hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls_image) 
        level = max(0, min(level, self.LEVEL_LIMIT))
        scale_factor = 1.0 - (level / float(self.LEVEL_LIMIT)) ** 1.5  # Exponential scaling
        
        l = cv2.multiply(l.astype(np.float32), scale_factor)
        l = np.clip(l, 0, 255).astype(np.uint8)
        
        hls_image = cv2.merge([h, l, s])
        
        return cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)

    
    def _degrade_image(self):
        match self.stage:
            case Stage.START:
                logger.debug(f"Degrading - {self.stage}")
                self.stage = Stage.BLACK_WHITE
                return self.current_image
            case Stage.BLACK_WHITE:
                if self.level < self.LEVEL_LIMIT:
                    self.level += self.level_steps
                    logger.debug(f"Degrading - {self.stage} - Level: {self.level - self.level_steps} -> {self.level} - Strenght: {self.level_steps}")
                    return self._apply_black_white(self.current_image, self.level)
                else:
                    self.stage = Stage.BLURRY
                    self.level = 0
                    return self.current_image
            case Stage.BLURRY:
                if self.level < self.LEVEL_LIMIT:
                    self.level += self.level_steps
                    logger.debug(f"Degrading - {self.stage} - Level: {self.level - self.level_steps} -> {self.level} - Strenght: {self.level_steps}")
                    return self._apply_blur(self.current_image, self.level)
                else:
                    self.stage = Stage.LIGHTNESS
                    self.level = 0
                    return self.current_image
            case Stage.LIGHTNESS:
                if self.level < self.LEVEL_LIMIT:
                    self.level += self.level_steps
                    logger.debug(f"Degrading - {self.stage} - Level: {self.level - self.level_steps} -> {self.level} - Strenght: {self.level_steps}")
                    return self._apply_darkness(self.current_image, self.level)
                else:
                    self.stage = Stage.END
                    self.level = self.LEVEL_LIMIT
                    return self.current_image
            case Stage.END:
                logger.debug(f"Degrading - Reached Stage: {self.stage}")
                return self.current_image
            case _:
                return self.current_image

    def _restore_image(self):
        """
        Gradually restore the image step by step, reversing the degradation stages.
        """
        match self.stage:
            case Stage.END:
                logger.debug(f"Restoring - Start from Stage: {self.stage}")
                self.stage = Stage.LIGHTNESS
                return self.current_image
            case Stage.LIGHTNESS:
                if self.level > 0:
                    self.level = max(0, self.level - self.level_steps)
                    logger.debug(f"Restoring - {self.stage} - Level: {self.level - self.level_steps} -> {self.level} - Strenght: {self.level_steps} Past Time: {int(time.time() - self.restoration_start_time)} - Remaining Time: {int(self.restoration_duration - (time.time() - self.restoration_start_time))}")
                    temp_image = self._apply_black_white(self.original_image, self.LEVEL_LIMIT)
                    temp_image = self._apply_blur(temp_image, self.LEVEL_LIMIT)
                    return self._apply_darkness(temp_image, self.level)
                else:
                    """
                    TODO: Die Data ist noch hard-coded. Müsste eigentlich in die Config aufgenommen werden
                    """
                    self.send_message(service_name = self.service_name, 
                                    data = {
                                        "time": 1,
                                        "pwm": 0.33
                                    }, 
                                    queue = self.outgoing_queue, 
                                    block = False,
                                    target_output = ServicesEnum.VibrationMotorOutput )
                    self.stage = Stage.BLURRY
                    self.level = self.LEVEL_LIMIT
                    return self.current_image
            case Stage.BLURRY:
                if self.level > 0:
                    self.level = max(0, self.level - self.level_steps)
                    logger.debug(f"Restoring - {self.stage} - Level: {self.level - self.level_steps} -> {self.level} - Strenght: {self.level_steps} Past Time: {int(time.time() - self.restoration_start_time)} - Remaining Time: {int(self.restoration_duration - (time.time() - self.restoration_start_time))}")
                    temp_image = self._apply_black_white(self.original_image, self.LEVEL_LIMIT)
                    return self._apply_blur(temp_image, self.level)
                else:
                    """
                    TODO: Die Data ist noch hard-coded. Müsste eigentlich in die Config aufgenommen werden
                    """
                    self.send_message(service_name = self.service_name, 
                                    data = {
                                        "time": 1,
                                        "pwm": 0.66
                                    }, 
                                    queue = self.outgoing_queue, 
                                    block = False,
                                    target_output = ServicesEnum.VibrationMotorOutput )
                    self.stage = Stage.BLACK_WHITE
                    self.level = self.LEVEL_LIMIT
                    return self.current_image
            case Stage.BLACK_WHITE:
                if self.level > 0:
                    self.level = max(0, self.level - self.level_steps)
                    logger.debug(f"Restoring - {self.stage} - Level: {self.level - self.level_steps} -> {self.level} - Strenght: {self.level_steps} Past Time: {int(time.time() - self.restoration_start_time)} - Remaining Time: {int(self.restoration_duration - (time.time() - self.restoration_start_time))}")
                    return self._apply_black_white(self.original_image, self.level)
                else:
                    """
                    TODO: Die Data ist noch hard-coded. Müsste eigentlich in die Config aufgenommen werden
                    """
                    self.send_message(service_name = self.service_name, 
                                    data = {
                                        "time": 1,
                                        "pwm": 1
                                    }, 
                                    queue = self.outgoing_queue, 
                                    block = False,
                                    target_output = ServicesEnum.VibrationMotorOutput )
                    self.stage = Stage.START
                    return self.current_image
            case Stage.START:
                logger.debug(f"Restoring - Reached Stage: {self.stage} Past Time: {int(time.time() - self.restoration_start_time)} - Remaining Time: {int(self.restoration_duration - (time.time() - self.restoration_start_time))}")
                return self.current_image
            case _:
                return self.current_image

    def _process_incoming_queue(self):
        """
        Process the incoming queue and update restoration values.
        """
        if not self.incoming_queue.qsize() == 0:
            message = self.receive_message(queue=self.incoming_queue)
            data = message.data
            self.restoration = True
            self.restoration_start_time = time.time()
            
            """ if message.service == ServicesEnum.TouchSensor.value and message.metadata and message.metadata.get("type"):
                # TODO: Hier muss dann die opacity vom overlay angepasst werden
                print(message.metadata["type"])
                return
            """
            if message.metadata and isinstance(message.metadata, dict):
                if "stage" in message.metadata:
                    self.stage = message.metadata["stage"]
                    logger.info(f"Stage updated to: {self.stage}")
            
            if isinstance(data, dict):
                if not self.reverse and data.get("time") and data.get("level_steps"): 
                    self.restoration_duration = data["time"]
                    self.level_steps = data["level_steps"]
                elif data.get("time") and data.get("level_steps"):
                    self.restoration_duration += data["time"] / self.difficulty
                    self.level_steps += data["level_steps"] / self.difficulty

    def _process_internal_queue(self):
        """
        Process the internal queue and display the current image.
        """
        if not self.internal_queue.qsize() == 0:
            current_image = self.receive_message(queue=self.internal_queue).data
            self._display_image(current_image)

    def _is_restoration_active(self):
        """
        Check if the restoration process is active based on time.
        """
        if self.restoration:
            elapsed_time = time.time() - self.restoration_start_time
            return elapsed_time < self.restoration_duration
        return False
    
    def _reset_restoration(self):
        """
        Reset restoration state.
        """
        self.restoration = False
        self.reverse = False
        self.level_steps = self.level_steps_init
