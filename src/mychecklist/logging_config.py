"""Logging setup for the MyChecklist application."""

from __future__ import annotations

import logging
from pathlib import Path

DEFAULT_LOG_FILENAME = "app.log"


def configure_logging(log_directory: Path, level: int = logging.INFO) -> Path:
    """Configure console and file logging and return the log file path."""
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / DEFAULT_LOG_FILENAME

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    if not any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_path.resolve()
        for handler in root_logger.handlers
    ):
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if not any(type(handler) is logging.StreamHandler for handler in root_logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    return log_path
