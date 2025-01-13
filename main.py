import logging
import time
from sensors.FaceRecognition import FaceRecognition
from sensors.TouchSensor import TouchSensor
from sensors.UltrasonicSensor import UltrasonicSensor
from outputs.ImageDisplayOutput import ImageDisplayOutput
from queue import Queue

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
       # logging.info(f"Received message from {message.service}: {message.data}")

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s :: %(name)-22s :: %(message)s")

    # Message Queues
    sensor_message_queue = Queue()
    output_message_queue = Queue()
    touch_message_queue = Queue()

    # Services
    services = [
        FaceRecognition(service_name = "Face Recognition", message_queue = sensor_message_queue, debug = False),
        UltrasonicSensor(service_name = "Ultrasonic Sensor", message_queue = sensor_message_queue, debug = False),
        TouchSensor(service_name = "Touch Sensor", message_queue = touch_message_queue, debug = False),
        ImageDisplayOutput(service_name = "Image Display Output", message_queue = output_message_queue)
    ]

    try:
        initialize_services(services)
        logging.info("All services started. Entering main loop")

        while True:
            time.sleep(1)
            process_messages(sensor_message_queue)
            process_messages(touch_message_queue)
            process_messages(output_message_queue)

            # image_display.trigger_action(10)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Shutting down...")
    finally:
        stop_services(services)
        logging.info("All services stopped. Exiting")
        

if __name__ == "__main__":
    main()