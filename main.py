import logging
from sensors.FaceRecognition import FaceRecognition
from dataclass.Message import Message
from queue import Queue

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    message_queue = Queue()
    fr_name = "FaceRecognition"
    face_recognition = FaceRecognition(
        service_name = fr_name, 
        message_queue = message_queue,
        debug = True
    )

    try:
        face_recognition.start()

        while True:
            message = message_queue.get()  # Retrieve Message object
            if isinstance(message, Message):
                logging.info(f"Received message from {message.service}: {message.data}")
                if message.service == fr_name:
                    detected_faces = message.data
                    logging.info(f"Detected faces: {detected_faces}")
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        face_recognition.stop()

if __name__ == "__main__":
    main()