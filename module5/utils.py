import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import colorlog
from datetime import datetime

"""Logger Setup"""
def log_run_header():
    separator = "=" * 50  # Adjust the length of the separator as needed
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"\n\n{separator}\nRun Start: {start_time}\n{separator}\n"
    logger.info(header)

logger = logging.getLogger(__name__) # Create the logger
logger.setLevel(logging.INFO) # Set the minimum level

LOG_DIRECTORY = "logs" # Define the directory for log file
LOG_FILENAME = "logs_report.log" # Define the filename
MAX_LOG_SIZE = 1024 * 1024 # 1 MB
BACKUP_COUNT = 3

# Ensure log directory exists
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create rotating file handler
log_file_path = os.path.join(LOG_DIRECTORY, LOG_FILENAME)
file_handler = RotatingFileHandler(log_file_path, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)

# Create colorlog stream handler for console output
stdout = colorlog.StreamHandler(stream=sys.stdout)

# Determine the format of the log entries for console
console_fmt = colorlog.ColoredFormatter(
    "%(name)s: %(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(blue)s%(filename)s:%(lineno)s%(reset)s | %(process)d >>> %(log_color)s%(message)s%(reset)s"
) 
stdout.setFormatter(console_fmt) # Set the formatting on the console logs
logger.addHandler(stdout) # Add the handler to the logger

# Set the format of log entries for file
file_fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s")
file_handler.setFormatter(file_fmt)

# Add file handler for file logging
logger.addHandler(file_handler) 
