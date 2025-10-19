# logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path("sorted_files_log.txt")


def setup_logger(level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch_formatter = logging.Formatter("%(message)s")
    ch.setFormatter(ch_formatter)

    # Rotating file handler
    fh = RotatingFileHandler(str(LOG_FILE), maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fh_formatter = logging.Formatter("[%Y-%m-%d %H:%M:%S] %(levelname)s: %(message)s")
    fh.setFormatter(fh_formatter)

    # Avoid duplicate handlers on repeated setup
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)
    else:
        # Replace handlers (helps in REPL/run cycles)
        logger.handlers = []
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
