import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging():
    profile = os.getenv("PROFILE", "dev").lower()
    log_format = "%(asctime)s %(levelname)s %(message)s"

    logger = logging.getLogger()

    if profile == "prod":
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            logger.removeHandler(handler)
        file_handler = RotatingFileHandler(
            "app.log",
            maxBytes=0,
            backupCount=20,
            encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    return logger
