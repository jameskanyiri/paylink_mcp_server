# tracing/logger.py
import logging
from pythonjsonlogger import jsonlogger
import os

LOG_DIR = "logs"
LOG_FILE = "paylink_trace.log"

#Ensure log directory exist
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("paylink_tracing")
logger.setLevel(logging.INFO)


# Create file handler
file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE))
file_handler.setLevel(logging.INFO)

# Use JSON formatter
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
)
file_handler.setFormatter(formatter)

# Avoid duplicate logs by clearing existing handlers
if not logger.handlers:
    logger.addHandler(file_handler)