"""Logging configuration for The Data Packet."""

import logging
import sys
from typing import Optional

from the_data_packet.core.config import get_config


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Log level override
    """
    config = get_config()
    level = log_level or config.log_level

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    # Set third-party loggers to WARNING to reduce noise
    for logger_name in ["requests", "urllib3", "boto3", "botocore", "anthropic"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
