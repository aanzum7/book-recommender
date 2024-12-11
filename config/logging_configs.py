import logging
import os
from datetime import datetime

# Directory for log files
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log file with current date as the filename
LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Logger instance
logger = logging.getLogger()
