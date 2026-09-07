import logging
import sys

def setup_logger():
    logger = logging.getLogger("agent_system")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler
        fh = logging.FileHandler("agent.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

logger = setup_logger()
