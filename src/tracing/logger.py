# tracing/logger.py
import logging
import sys
from pythonjsonlogger import jsonlogger

logger = logging.getLogger("paylink_tracing")
logger.setLevel(logging.INFO)

# Create stream handler for stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

# Use JSON formatter
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
)
stream_handler.setFormatter(formatter)

# Avoid duplicate logs by clearing existing handlers and adding the new one
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(stream_handler)
