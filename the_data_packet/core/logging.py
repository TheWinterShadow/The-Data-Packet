"""Centralized logging configuration for The Data Packet.

This module provides unified logging setup for the entire application.
It configures structured logging with proper formatters, reduces noise from
third-party libraries, and provides a consistent interface for obtaining
logger instances throughout the codebase.

Features:
    - Structured logging with timestamps and module names
    - Configurable log levels via environment variables
    - Noise reduction from third-party libraries
    - Consistent format across all modules
    - Console output optimized for Docker containers

Usage:
    # In main application entry point
    setup_logging()

    # In any module
    from the_data_packet.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("Processing started")

Log Levels:
    DEBUG: Detailed debugging information
    INFO: General operational messages
    WARNING: Warning messages for recoverable issues
    ERROR: Error messages for serious problems
    CRITICAL: Critical errors that may cause shutdown
"""

import logging
import sys
from typing import Optional

from the_data_packet.core.config import get_config


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure application-wide logging settings.

    Sets up structured logging with consistent formatting, configurable
    log levels, and noise reduction from third-party libraries. Should be
    called once at application startup.

    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, uses configuration default. Case insensitive.

    Example:
        # Use default log level from config
        setup_logging()

        # Override to DEBUG level
        setup_logging("DEBUG")

        # From environment variable
        setup_logging(os.getenv("LOG_LEVEL"))

    Note:
        This function uses force=True to override any existing logging
        configuration, ensuring consistent behavior in all environments.
    """
    config = get_config()

    # Use provided level or fall back to config default
    level = log_level or config.log_level

    # Convert string level to logging constant, default to INFO if invalid
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger with structured format
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,  # Explicit stdout for container compatibility
        force=True,  # Override any existing configuration
    )

    # Reduce noise from third-party libraries to prevent log spam
    # These libraries are verbose at DEBUG/INFO levels
    third_party_loggers = [
        "requests",  # HTTP library used by all API clients
        "urllib3",  # Underlying HTTP transport
        "boto3",  # AWS SDK
        "botocore",  # AWS SDK core
        "anthropic",  # Claude API client
        "google",  # Google API clients
        "feedparser",  # RSS parsing library
    ]

    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance for a module.

    This is the standard way to obtain logger instances throughout the
    application. Use __name__ as the logger name to get hierarchical
    logger names that match the module structure.

    Args:
        name: Logger name, typically __name__ from calling module

    Returns:
        Configured logger instance ready for use

    Example:
        # Standard usage in any module
        from the_data_packet.core.logging import get_logger
        logger = get_logger(__name__)

        # Usage examples
        logger.info("Starting article collection")
        logger.warning("Article content is short: %d chars", len(content))
        logger.error("Failed to generate script: %s", str(error))

        # With structured data (for log aggregation)
        logger.info("Article processed", extra={
            "article_id": article.id,
            "processing_time": elapsed_seconds
        })

    Note:
        Logger names follow Python's hierarchical naming convention.
        For example, 'the_data_packet.sources.wired' will inherit
        configuration from 'the_data_packet.sources' and 'the_data_packet'.
    """
    return logging.getLogger(name)
