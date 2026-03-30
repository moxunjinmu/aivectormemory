import logging
import sys


def _setup_logger(level: str = "WARNING") -> logging.Logger:
    logger = logging.getLogger("aivectormemory")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.WARNING))
    return logger


log = _setup_logger()
