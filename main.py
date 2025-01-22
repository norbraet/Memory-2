import logging
import colorlog
from controller.OutputController import OutputController
from enums.ServicesEnum import ServicesEnum

logger = logging.getLogger(__name__)

def setup_logging():
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s | %(name)-26s | %(message)s",
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    console_handler.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler],
    )

def main():
    setup_logging()
    
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