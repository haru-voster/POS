import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

class LogService:
    LOG_DIR = "logs"

    @staticmethod
    def get_log_file(log_type="error"):
        if not os.path.exists(LogService.LOG_DIR):
            os.makedirs(LogService.LOG_DIR)
        current_date = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(LogService.LOG_DIR, f"{log_type}-{current_date}.log")

    @staticmethod
    def setup_logger(log_type, log_level):
        logger = logging.getLogger(log_type)
        logger.setLevel(log_level)

        log_file = LogService.get_log_file(log_type)
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(file_handler)

        return logger

    @staticmethod
    def log_error(message, exc=None):
        error_logger = LogService.setup_logger("error", logging.ERROR)
        error_logger.error(message, exc_info=exc is not None)

    @staticmethod
    def log_info(message):
        info_logger = LogService.setup_logger("info", logging.INFO)
        info_logger.info(message)
