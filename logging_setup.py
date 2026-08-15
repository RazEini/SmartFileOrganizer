"""
Logging configuration for the Smart File Organizer.
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_FILE = Path("sorted_files_log.txt")
SETTINGS_FILE = Path("organizer_settings.json")


def setup_logger(level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger("smart_organizer")
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(message)s"))

    fh = RotatingFileHandler(
        str(LOG_FILE),
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
        mode="a"
    )
    fh.setLevel(level)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
    )

    logger.handlers = []
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False

    return logger


logger = setup_logger()
