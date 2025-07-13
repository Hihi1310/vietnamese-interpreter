import logging
import os
from datetime import datetime
import pytz


def setup_logger(name, log_file, log_level='INFO'):
    """
    Setup a logger with GMT+7 timezone formatting
    
    Args:
        name (str): Logger name (e.g., 'transcription', 'translation')
        log_file (str): Path to the log file
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    gmt7 = pytz.timezone('Asia/Bangkok')
    
    class GMT7Formatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, tz=gmt7)
            return dt.strftime('%Y-%m-%d %H:%M:%S GMT+7')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent adding multiple handlers if logger already exists
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        formatter = GMT7Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
