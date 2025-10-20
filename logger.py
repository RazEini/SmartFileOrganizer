import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path("sorted_files_log.txt")

def setup_logger(level=logging.INFO) -> logging.Logger:
    """
    Returns a configured root logger. Uses a console handler and rotating file handler.
    """
    logger = logging.getLogger("smart_organizer")
    logger.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch_formatter = logging.Formatter("%(message)s")
    ch.setFormatter(ch_formatter)

    # Rotating file handler - consistent timestamp format
    fh = RotatingFileHandler(str(LOG_FILE), maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(level)
    fh_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fh_formatter)

    # Replace existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False
    return logger
