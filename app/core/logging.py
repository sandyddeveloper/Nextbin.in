import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging(process_name: str):
    """
    Sets up a structured rotating logging configuration.
    Identifies if it's the 'api' or 'worker' process to route logs safely
    without triggering Windows sharing violations/file lock issues.
    """
    root_logger = logging.getLogger()
    # Set default level
    root_logger.setLevel(logging.INFO)
    
    # Clear any default pre-existing handlers to prevent double logs
    root_logger.handlers = []
    
    # Formatter configuration
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 1. Console Handler (Keeps logs visible in nila.py console)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # 2. General info.log (Process-specific to prevent concurrent file locking errors)
    info_log_filename = f"info_{process_name}.log"
    info_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, info_log_filename),
        maxBytes=5 * 1024 * 1024,  # 5MB Max Size
        backupCount=3,
        encoding="utf-8"
    )
    info_handler.setFormatter(formatter)
    info_handler.setLevel(logging.INFO)
    root_logger.addHandler(info_handler)
    
    # 3. Process-specific Detailed Logs routing
    if process_name == "api":
        # API Log file
        api_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "api.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        api_handler.setFormatter(formatter)
        api_handler.setLevel(logging.INFO)
        
        # Attach to uvicorn and app API logs
        logging.getLogger("nextbin.api").addHandler(api_handler)
        logging.getLogger("uvicorn.error").addHandler(api_handler)
        logging.getLogger("uvicorn.access").addHandler(api_handler)
        
    elif process_name == "worker":
        # Worker Log file
        worker_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "worker.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        worker_handler.setFormatter(formatter)
        worker_handler.setLevel(logging.INFO)
        
        # Attach to Huey and modular worker tasks
        logging.getLogger("huey").addHandler(worker_handler)
        logging.getLogger("nextbin.worker").addHandler(worker_handler)
        logging.getLogger("nextbin.instagram").addHandler(worker_handler)
        logging.getLogger("nextbin.monitoring").addHandler(worker_handler)
        logging.getLogger("nextbin.blog").addHandler(worker_handler)
