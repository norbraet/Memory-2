import logging
import time
from enum import Enum
from sensors.FaceRecognition import FaceRecognition
from sensors.TouchSensor import TouchSensor
from sensors.UltrasonicSensor import UltrasonicSensor
from outputs.ImageDisplayOutput import ImageDisplayOutput
from queue import Queue

class Services(Enum):
    FaceRecognition = "Face Recognition"
    UltrasonicSensor = "Ultrasonic Sensor"
    TouchSensor = "Touch Sensor"
    ImageDisplayOutput = "Image Display Output"

def initialize_services(services):
    """
    Initialize and start all services in the provided list.
    """
    for service in services:
        service.start()

def stop_services(services):
    """
    Stop and clean up all services in the provided list.
    """
    for service in services:
        try:
            service.stop()
        except KeyboardInterrupt:
            logging.warning(f"Interrupted while stopping {service.service_name}")

def process_messages(message_queue):
    """
    Process messages from the message queue.
    """
    while not message_queue.empty():
        message = message_queue.get()
        logging.info(f"Received message from {message.service}: {message.data}")

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s :: %(name)-22s :: %(message)s")

    # Message Queues
    sensor_message_queue = Queue()
    output_message_queue = Queue()
    touch_message_queue = Queue()

    # Services
    services = {
        Services.FaceRecognition: FaceRecognition(service_name = Services.FaceRecognition.value, message_queue = sensor_message_queue, debug = False),
        Services.UltrasonicSensor: UltrasonicSensor(service_name = Services.UltrasonicSensor.value, message_queue = sensor_message_queue, debug = False),
        Services.TouchSensor: TouchSensor(service_name = Services.TouchSensor.value, message_queue = touch_message_queue, debug = False),
        Services.ImageDisplayOutput: ImageDisplayOutput(service_name = Services.ImageDisplayOutput.value, message_queue = output_message_queue)
    }

    try:
        initialize_services(services.values())
        logging.info("All services started. Entering main loop")

        services[Services.ImageDisplayOutput].trigger_action()

        while True:
            time.sleep(1)
            process_messages(sensor_message_queue)
            process_messages(touch_message_queue)
            process_messages(output_message_queue)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Shutting down...")
    finally:
        stop_services(services.values())
        logging.info("All services stopped. Exiting")
        

if __name__ == "__main__":
    main()