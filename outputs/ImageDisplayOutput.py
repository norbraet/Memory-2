import cv2
import queue
import time
from sensors.BaseSensor import BaseSensor

class ImageDisplayOutput(BaseSensor):
    def __init__(self, service_name, message_queue=None, config=None, debug=False, image_path="./assets/image.png"):
        """
        A sensor-like class for displaying images, extending BaseSensor.
        :param service_name: Unique name for the service.
        :param message_queue: Shared queue for communication.
        :param config: Optional configuration dictionary.
        :param debug: Enable debugging logs.
        :param image_path: Path to the initial image.
        """
        super().__init__(service_name, message_queue, config, debug)
        self.window_name = "Image Display"
        self.image_path = image_path
        self.current_image = None
        self.update_queue = queue.Queue()

    def setup(self):
        """
        Perform setup tasks, like loading the initial image and setting up the display window.
        """
        self._logger.info("Setting up ImageDisplayOutput")
        cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        self.current_image = cv2.imread(self.image_path)

        if self.current_image is None:
            self._logger.error(f"Failed to load image from path: {self.image_path}")
        else:
            self._logger.info("Initial image loaded successfully.")
            cv2.imshow(self.window_name, self.current_image)
            cv2.waitKey(1)  # Ensure the initial image is displayed



    def loop(self):
        """
        Main loop for the image display service.
        Continuously checks for new images in the update queue and updates the display.
        """
        try:
            while not self._stop_event.is_set():
                if not self.update_queue.empty():
                    queue_item = self.update_queue.get()
                    if queue_item is not None:
                        self.trigger_action(queue_item)
                time.sleep(0.1)
        except Exception as e:
            self._logger.error(f"Error reading queue item: {e}")


    def trigger_action(self, data):
        """
        Applies the filter to the current image based on the provided data.
        """
        if self.current_image is not None:
            self.current_image = self.apply_black_white(self.current_image, data)
            cv2.imshow(self.window_name, self.current_image)
            cv2.waitKey(1)
        else:
            self._logger.error("No image loaded to apply action.")


    def cleanup(self):
        """
        Clean up resources, like destroying the display window.
        """
        self._logger.info("Cleaning up ImageDisplayOutput")
        cv2.destroyWindow(self.window_name)
    
    def update_image(self, image):
        """
        Add a new image to the update queue to be displayed.
        :param image: The new image to display.
        """
        if image is not None:
            self.update_queue.put(image)
            self._logger.info("Image updated.")

    def apply_black_white(self, image, level):
        """
        Gradually convert the image to black and white, or restore color.
        :param image: The original image.
        :param level: Percentage of black and white to apply (0-100%).
        """
        hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls_image)

        
        s = cv2.multiply(s, (100 - level) / 100.0)

        
        self._logger.debug(f"Applied black & white filter with level {level}% saturation reduction")

        hls_image = cv2.merge([h, l, s])
        black_white_image = cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)
        
        return black_white_image

    def apply_blur(self, image, level):
        """
        Gradually apply a blur filter, or restore sharpness.
        :param image: The image to blur.
        :param level: The current blur level (0 to 10).
        """
        kernel_size = 3 + (level * 2)  # Kernel size: 3, 5, 7, ..., 21
        if kernel_size > 21:
            kernel_size = 21

        if self.blur_direction == 'negative':
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif self.blur_direction == 'positive' and level > 0:
            return cv2.GaussianBlur(image, (max(3, kernel_size - 2), max(3, kernel_size - 2)), 0)
        return image

    def apply_brightness(self, image, level):
        """
        Gradually apply brightness change, or reduce brightness.
        :param image: The image to adjust brightness.
        :param level: The current brightness level (0 to 10).
        """
        alpha = 1.0  # No contrast change
        if self.brightness_direction == 'negative':
            beta = 10 * level  # Decrease brightness
        elif self.brightness_direction == 'positive':
            beta = -10 * level  # Increase brightness
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


