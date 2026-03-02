"""
File: fuzzhub/utils/logging.py
"""

import logging
import os

LOG_DIR = os.path.expanduser(".")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "fuzzhub.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
    ],
)

def get_logger(name: str):
    return logging.getLogger(name)
