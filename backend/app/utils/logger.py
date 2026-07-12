"""Reusable logging utility for the application."""

import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger instance.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.
              Defaults to the root application logger.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    logger_name = name or "ai_debate_arena"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
