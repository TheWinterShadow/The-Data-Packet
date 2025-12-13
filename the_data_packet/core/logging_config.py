"""Logging configuration for The Data Packet package."""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_settings() -> DummySettings:
    """Placeholder for settings - avoid circular import."""

    class DummySettings:
        log_level = "INFO"
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    return DummySettings()


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> None:
    """
    Setup package-wide logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
        format_string: Custom log format string
    """
    settings = get_settings()

    # Use provided values or defaults from settings
    log_level = level or settings.log_level
    log_format = format_string or settings.log_format

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Get root logger for the package
    logger = logging.getLogger("the_data_packet")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Logging initialized at {log_level} level")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the package name prefix.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"the_data_packet.{name}")
