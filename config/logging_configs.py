import os
import sys
import logging
from datetime import datetime

# Directory for persistent logs
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Log file named with current date (e.g. 2026-09-05.log)
LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# Standardized high-readability formatter
LOG_FORMAT = "[%(asctime)s] [%(levelname)-7s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configure root logger safely to prevent any accidental stdout/stderr console prints
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)
for h in list(root_logger.handlers):
    root_logger.removeHandler(h)
root_logger.addHandler(logging.NullHandler())

# Configure dedicated NovelNexus file-only logger
logger = logging.getLogger("NovelNexus")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(file_handler)

logger.propagate = False
