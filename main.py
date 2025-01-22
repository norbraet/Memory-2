import logging
from controller.OutputController import OutputController
from enums.ServicesEnum import ServicesEnum

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s :: %(name)-22s :: %(message)s")
    
    logic = OutputController(service_name="Logic", debug=False)

    try:
        logic.start()

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Shutting down...")
    finally:
        logic.stop()
        logging.info("All services stopped. Exiting")
        

if __name__ == "__main__":
    main()