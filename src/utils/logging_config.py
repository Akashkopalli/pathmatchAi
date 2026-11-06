"""PathMatch AI - Logging Configuration.

Provides structured application logging and execution monitoring.
"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "pathmatch", log_level: int = logging.INFO) -> logging.Logger:
    """Configure and return an application logger."""
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(log_level)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()

