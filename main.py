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
    faces_detection = None
    distance_detection = None

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

    try:
        face_recognition.start()
        ultrasonic_sensor.start()

        while True:
            message = message_queue.get()  # Retrieve Message object
            if isinstance(message, Message):
                logging.info(f"Received message from {message.service}: {message.data}")
                match message.service:
                    case "FaceRecognition":
                        # Handle the message data for the FaceRecognitionService
                        faces_detection = message.data
                        # Do Something
                        logging.info(f"Faces detected.")
                        faces_detection = None
                        pass
                    case "UltrasonicSensor":
                        if distance_detection is not None and message.data < distance_detection + 10:
                            # Do Something
                            logging.info(f"Distance changed from {distance_detection} to {message.data}")
                        else:
                            distance_detection = message.data
                        pass
                    case _:
                        # Handle other services or unmatched services
                        logging.warning(f"Unknown service: {message.service}")
                        pass
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        face_recognition.stop()
        ultrasonic_sensor.stop()

if __name__ == "__main__":
    main()