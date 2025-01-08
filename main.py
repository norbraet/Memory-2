import logging
from services.FaceRecognitionService import FaceRecognitionService

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    fr_service = FaceRecognitionService()
    
    try:
        fr_service.start_camera()
        fr_service.run_in_background()

        while True:
            # Check for detected faces in the queue
            detected_faces = fr_service.get_detected_faces()
            if detected_faces is not None and len(detected_faces) > 0:
                logging.info(f"Detected faces: {detected_faces}")
                # Main program logic to handle faces can go here
            else:
                logging.debug("No faces detected at this time.")
            
            """ time.sleep(0.1)  # Optional, to control the loop interval """

    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    finally:
        fr_service.stop_service()