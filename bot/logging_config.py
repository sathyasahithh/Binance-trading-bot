"""
Logging configuration module for the trading bot.
Ensures the log directory exists and configures file-based logging.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = "logs/trading.log") -> None:
    """
    Configures the application logger to write logs to a rotating log file.
    
    Args:
        log_file (str): Absolute or relative path to the log file.
    """
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        
    root_logger = logging.getLogger()
    
    # Set standard logging level
    root_logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers if re-initialized
    if root_logger.handlers:
        return
        
    # Configure file handler (rotating, max 5MB, utf-8 encoding)
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # Fallback to simple stdout if file writing is restricted
        logging.basicConfig(level=logging.INFO)
        logging.warning("Could not set up file logging handler, falling back to stdout: %s", e)
