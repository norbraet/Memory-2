import logging
import time

from controller.OutputController import OutputController
from dataclass.ServicesEnum import ServicesEnum

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s :: %(name)-22s :: %(message)s")
    
    logic = OutputController(service_name="Logic", debug=False)

    try:
        logic.start()

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
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Shutting down...")
    finally:
        logic.stop()
        logging.info("All services stopped. Exiting")
        

if __name__ == "__main__":
    main()