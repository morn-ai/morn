import logging
import os
import uvicorn
import sys

from fastapi import FastAPI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def configure_logger():
    profile = os.getenv("PROFILE", "dev").lower()
    log_format = "%(asctime)s %(levelname)s %(message)s"
    if profile == "prod":
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            logger.removeHandler(handler)
        file_handler = logging.FileHandler("app.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)


configure_logger()

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
