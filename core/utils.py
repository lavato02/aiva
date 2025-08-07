import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/actions.log",
        maxBytes=1024*1024,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)