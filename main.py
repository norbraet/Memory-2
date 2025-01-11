import logging
from sensors.FaceRecognition import FaceRecognition
from sensors.UltrasonicSensor import UltrasonicSensor
from dataclass.Message import Message
from queue import Queue

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    message_queue = Queue()
    fr_name = "FaceRecognition"
    uss_name = "UltrasonicSensor"

    face_recognition = FaceRecognition(
        service_name = fr_name, 
        message_queue = message_queue,
        debug = True
    )

    ultrasonic_sensor = UltrasonicSensor(
        service_name = uss_name,
        message_queue= message_queue,
        debug = True
    )

    try:
        face_recognition.start()
        ultrasonic_sensor.start()

        while True:
            message = message_queue.get()  # Retrieve Message object
            if isinstance(message, Message):
                logging.info(f"Received message from {message.service}: {message.data}")
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        face_recognition.stop()
        ultrasonic_sensor.stop()

if __name__ == "__main__":
    main()