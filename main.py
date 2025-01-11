import logging
import time
from sensors.FaceRecognition import FaceRecognition
from sensors.UltrasonicSensor import UltrasonicSensor
from outputs.ImageDisplayOutput import ImageDisplayOutput
from dataclass.Message import Message
from queue import Queue

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    message_queue = Queue()
    message_output_queue = Queue()
    fr_name = "FaceRecognition"
    uss_name = "UltrasonicSensor"
    ido_name = "Image Display Output"

    #Sensor
    face_recognition = FaceRecognition(
        service_name = fr_name, 
        message_queue = message_queue,
        debug = False
    )

    ultrasonic_sensor = UltrasonicSensor(
        service_name = uss_name,
        message_queue= message_queue,
        debug = False
    )

    #Output
    image_display = ImageDisplayOutput(
        service_name="ImageDisplay", 
        message_queue=message_output_queue, 
        image_path="./assets/image.png")

    try:
        face_recognition.start()
        ultrasonic_sensor.start()
        image_display.start()
        while True:
            time.sleep(1)
            image_display.trigger_action(10)

        while True:
            message = message_queue.get()  # Retrieve Message object
            """ if isinstance(message, Message):
                logging.info(f"Received message from {message.service}: {message.data}") """
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        face_recognition.stop()
        ultrasonic_sensor.stop()
        image_display.stop()
        

if __name__ == "__main__":
    main()