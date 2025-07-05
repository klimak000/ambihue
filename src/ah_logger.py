import logging


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on severity level."""

    # Define color codes for different log levels
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"  # Reset color

    def format(self, record: logging.LogRecord) -> str:
        # Add color to the log level name
        lvl_color = self.COLORS.get(record.levelname, self.RESET)

        record.levelname = lvl_color + record.levelname + self.RESET

        record.module = lvl_color + record.module[:18].center(18) + self.RESET

        return super().format(record)


def init_logger(loglevel: str) -> None:
    # Define a custom format including milliseconds
    log_format = "%(asctime)s.%(msecs)03d %(levelname)17s %(module)20s - %(message)s"
    date_format = "%H:%M:%S"

    # Create a handler with the ColoredFormatter
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter(fmt=log_format, datefmt=date_format))

    # Configure the logger
    logger = logging.getLogger()
    logger.setLevel(loglevel)  # Set the logging level to DEBUG
    logger.addHandler(handler)

    # Print all types of messages
    if loglevel == "DEBUG":
        logger.debug("This is a debug message.")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.critical("This is a critical message.")
