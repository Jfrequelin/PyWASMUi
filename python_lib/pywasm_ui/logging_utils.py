from __future__ import annotations

import logging
import os

_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_LOG_LEVELS: dict[str, int] = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def configure_logging() -> None:
    """Configure project logging once using PYWASM_LOG_LEVEL.

    The default level is INFO. Invalid values fallback to INFO.
    """

    root = logging.getLogger()
    if root.handlers:
        return

    raw_level = os.getenv("PYWASM_LOG_LEVEL", "INFO").strip().upper()
    level = _LOG_LEVELS.get(raw_level, logging.INFO)
    logging.basicConfig(level=level, format=_DEFAULT_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
