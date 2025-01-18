import logging
import time
from enum import Enum
from sensors.FaceRecognition import FaceRecognition
from sensors.TouchSensor import TouchSensor
from sensors.UltrasonicSensor import UltrasonicSensor
from outputs.ImageDisplayOutput import ImageDisplayOutput
from queue import Queue
from dataclass.Message import Message

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

def printout_messages(message_queue):
    """
    Printout messages from the message queue.
    """
    while not message_queue.empty():
        message = message_queue.get()
        logging.info(f"Received message from {message.service}: {message.data}")

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s :: %(name)-22s :: %(message)s")

    # Message Queues
    display_outgoing_queue = Queue()
    display_incoming_queue = Queue()

    touch_outgoing_queue = Queue()
    touch_incoming_queue = Queue()

    ultrasonic_outgoing_queue = Queue()
    ultrasonic_incoming_queue = Queue()

    facerecognition_outgoing_queue = Queue()
    facerecognition_incoming_queue = Queue()


    # Services
    services = {
        # Services.FaceRecognition: FaceRecognition(service_name = Services.FaceRecognition.value, message_queue = sensor_message_queue, debug = False),
        # Services.UltrasonicSensor: UltrasonicSensor(service_name = Services.UltrasonicSensor.value, message_queue = sensor_message_queue, debug = False),
        # Services.TouchSensor: TouchSensor(service_name = Services.TouchSensor.value, message_queue = touch_message_queue, debug = False),
        Services.ImageDisplayOutput: ImageDisplayOutput(service_name = Services.ImageDisplayOutput.value, outgoing_queue = display_outgoing_queue, incoming_queue = display_incoming_queue)
    }

    try:
        initialize_services(services.values())
        logging.info("All services started. Entering main loop")

        services[Services.ImageDisplayOutput].trigger_action()

        """
        Der Grund warum der nicht in die while Schleife reingeht, ist weil die .trigger_action() selbst eine while True schleife ist und der Code nie an den unteren Punkt kommt.
        Um das zu lösen, muss ein weiterer Thread erstellt werden, nämlich die Logic Thread.

        Müsste dann ungefährt so aussehen:


                                         _______________
                                        |               |
                                        | Sensor Thread |
                                        |_______________|
                                            Sensor 1
                                        
                                                ^
                                                |
                                                |
         _____________                   ______________                   _________________________
        |             |                 |              |                 |                         |
        | Main Thread |       ---->     | Logic Thread |       ---->     | Image Processing Thread |
        |_____________|                 |______________|                 |_________________________|
         Frontend (GUI)                      Backend                                Backend

                                                |
                                                |
                                                V
                                         _______________
                                        |               |
                                        | Sensor Thread |       
                                        |_______________|
                                             Sensor 2
        
        Das bedeutet, dass die GUI nur die Logik kennt und diese auch initialisiert über logic.start(). Die Logic kennt alle Sensor und Output objekte und dirigiert dessen Verhalten über die Queue.
        Es müssen nicht alle Queues vorliegen als Objekte, sondern es würde reichen wenn die Queues über die Objekte selbst erreichbar sind. Das bedeutet aber auch, dass die MessageService.py die Queues
        nicht durchgereicht werden muss, sondern die Objekte selbst die eigene Queue instanziieren. 
        
        
        """
        
        while True:
            time.sleep(5)
            print("Dingdong")
            """ services[Services.ImageDisplayOutput].send_message(
                service_name = services[Services.ImageDisplayOutput].service_name,
                data = "Hello",
                queue = services[Services.ImageDisplayOutput].incoming_queue
            ) """
            # display_incoming_queue.put(Message(service = services[Services.ImageDisplayOutput].service_name, data = {str: "Hello"}))
            
            # printout_messages(sensor_message_queue)
            # printout_messages(touch_message_queue)
            # printout_messages(display_outgoing_queue)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Shutting down...")
    finally:
        stop_services(services.values())
        logging.info("All services stopped. Exiting")
        

if __name__ == "__main__":
    main()