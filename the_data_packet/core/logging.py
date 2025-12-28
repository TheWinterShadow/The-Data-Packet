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

import json
import logging
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from the_data_packet.utils.s3 import S3Storage

from the_data_packet.core.config import Config, get_config


class JSONLHandler(logging.Handler):
    """
    Custom logging handler that writes log entries to JSONL files.

    Features:
    - Writes structured JSON logs to .jsonl files
    - Automatically rotates files daily
    - Includes metadata like timestamp, module, level
    - Thread-safe file operations
    """

    def __init__(self, log_dir: str = "output/logs"):
        super().__init__()
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        """Write log record as JSON line to daily log file."""
        try:
            with self._lock:
                # Create daily log file
                log_date = datetime.now().strftime("%Y-%m-%d")
                log_file = self.log_dir / f"the-data-packet-{log_date}.jsonl"

                # Convert log record to JSON
                log_data = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                # Add extra fields if present
                if hasattr(record, "__dict__"):
                    for key, value in record.__dict__.items():
                        if key not in log_data and not key.startswith("_"):
                            # Skip standard logging fields
                            if key not in [
                                "name",
                                "msg",
                                "args",
                                "levelname",
                                "levelno",
                                "pathname",
                                "filename",
                                "module",
                                "lineno",
                                "funcName",
                                "created",
                                "msecs",
                                "relativeCreated",
                                "thread",
                                "threadName",
                                "processName",
                                "process",
                                "getMessage",
                                "exc_info",
                                "exc_text",
                                "stack_info",
                            ]:
                                try:
                                    # Only add JSON-serializable values
                                    json.dumps(value)
                                    log_data[key] = value
                                except (TypeError, ValueError):
                                    log_data[key] = str(value)

                # Add exception info if present
                if record.exc_info:
                    log_data["exception"] = self.format(record)

                # Write to file
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_data, separators=(",", ":")) + "\n")

        except Exception:
            # Don't let logging errors crash the application
            self.handleError(record)


class S3LogUploader:
    """
    Background service to upload JSONL log files to S3.

    Features:
    - Monitors log directory for completed daily logs
    - Uploads files to S3 with structured naming
    - Optionally removes local files after upload
    - Runs in background thread
    """

    def __init__(
        self,
        log_dir: str = "output/logs",
        upload_interval: int = 3600,
        remove_after_upload: bool = False,
    ):
        """
        Initialize S3 log uploader.

        Args:
            log_dir: Directory containing JSONL log files
            upload_interval: How often to check for files to upload (seconds)
            remove_after_upload: Whether to delete local files after upload
        """
        self.log_dir = Path(log_dir)
        self.upload_interval = upload_interval
        self.remove_after_upload = remove_after_upload
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._s3_storage: Optional["S3Storage"] = None

    def start(self) -> None:
        """Start background upload service."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._upload_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop background upload service."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=10)

    def _get_s3_storage(self) -> Optional["S3Storage"]:
        """Lazy initialize S3 storage to avoid import issues."""
        if self._s3_storage is None:
            try:
                from the_data_packet.utils.s3 import S3Storage

                self._s3_storage = S3Storage()
            except Exception as e:
                # S3 not configured, skip uploads
                logging.getLogger(__name__).warning(
                    f"S3 not available for log uploads: {e}"
                )
                return None
        return self._s3_storage

    def _upload_loop(self) -> None:
        """Main upload loop running in background thread."""
        logger = logging.getLogger(f"{__name__}.uploader")

        while not self._stop_event.wait(self.upload_interval):
            try:
                self._upload_completed_logs()
            except Exception as e:
                logger.error(f"Error in log upload loop: {e}")

    def _upload_completed_logs(self) -> None:
        """Upload completed daily log files to S3."""
        logger = logging.getLogger(f"{__name__}.uploader")

        if not self.log_dir.exists():
            return

        s3_storage = self._get_s3_storage()
        if s3_storage is None:
            return

        # Find JSONL files that are from previous days (completed)
        today = datetime.now().strftime("%Y-%m-%d")

        for log_file in self.log_dir.glob("the-data-packet-*.jsonl"):
            # Skip today's log file as it might still be written to
            if today in log_file.name:
                continue

            try:
                # Upload to S3 with structured path: logs/YYYY/MM/DD/filename.jsonl
                date_str = log_file.stem.replace("the-data-packet-", "")
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                s3_key = f"logs/{date_obj.year:04d}/{date_obj.month:02d}/{date_obj.day:02d}/{log_file.name}"

                result = s3_storage.upload_file(
                    local_path=log_file,
                    s3_key=s3_key,
                    content_type="application/x-ndjson",
                )

                if result.success:
                    logger.info(f"Uploaded log file to S3: {result.s3_url}")

                    # Remove local file if configured
                    if self.remove_after_upload:
                        log_file.unlink()
                        logger.info(f"Removed local log file: {log_file}")
                else:
                    logger.error(
                        f"Failed to upload log file {log_file}: {result.error_message}"
                    )

            except Exception as e:
                logger.error(f"Error uploading log file {log_file}: {e}")


# Global S3 uploader instance
_s3_uploader: Optional[S3LogUploader] = None


def setup_logging(
    log_level: Optional[str] = None,
    enable_jsonl: Optional[bool] = None,
    enable_s3_upload: Optional[bool] = None,
    log_dir: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging settings.

    Sets up structured logging with consistent formatting, configurable
    log levels, and noise reduction from third-party libraries. Should be
    called once at application startup.

    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, uses configuration default. Case insensitive.
        enable_jsonl: Whether to enable JSONL file logging (default: from config)
        enable_s3_upload: Whether to enable S3 upload of log files (default: from config)
        log_dir: Directory for JSONL log files (default: from config)

    Example:
        # Use default settings from config
        setup_logging()

        # Override to DEBUG level, disable S3 upload
        setup_logging("DEBUG", enable_s3_upload=False)

        # Console only (no JSONL files)
        setup_logging(enable_jsonl=False, enable_s3_upload=False)

    Note:
        This function uses force=True to override any existing logging
        configuration, ensuring consistent behavior in all environments.
        JSONL logs include structured metadata for log aggregation and analysis.
        S3 upload runs in background and uploads completed daily log files.
    """
    global _s3_uploader

    config = get_config()

    # Use provided parameters or fall back to config defaults
    # Handle both real config and mocked config for tests
    level = log_level or getattr(config, "log_level", "INFO")

    # Handle config attributes that might be mocked
    if enable_jsonl is not None:
        enable_jsonl_logging = enable_jsonl
    else:
        enable_jsonl_logging = getattr(config, "enable_jsonl_logging", True)

    if enable_s3_upload is not None:
        enable_s3_log_upload = enable_s3_upload
    else:
        enable_s3_log_upload = getattr(config, "enable_s3_log_upload", True)
        # Disable S3 upload during tests to avoid thread issues
        if "pytest" in sys.modules:
            enable_s3_log_upload = False

    if log_dir is not None:
        logs_directory = log_dir
    else:
        logs_directory = getattr(config, "log_dir", "output/logs")
        # Ensure we have a string, not a Mock object
        if not isinstance(logs_directory, (str, Path)):
            logs_directory = "output/logs"

    # Convert string level to logging constant, default to INFO if invalid
    numeric_level = getattr(logging, str(level).upper(), logging.INFO)

    # Configure root logger with structured format
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,  # Explicit stdout for container compatibility
        force=True,  # Override any existing configuration
    )

    # Add JSONL file handler if enabled
    if enable_jsonl_logging:
        root_logger = logging.getLogger()
        jsonl_handler = JSONLHandler(logs_directory)
        jsonl_handler.setLevel(numeric_level)
        root_logger.addHandler(jsonl_handler)

        logger = logging.getLogger(__name__)
        logger.info(f"JSONL logging enabled, writing to: {logs_directory}")

        # Start S3 uploader if enabled
        if enable_s3_log_upload:
            try:
                if _s3_uploader:
                    _s3_uploader.stop()

                upload_interval = getattr(config, "log_upload_interval", 3600)
                remove_after_upload = getattr(
                    config, "remove_logs_after_upload", False)

                # Ensure numeric values for thread safety
                if not isinstance(upload_interval, int):
                    upload_interval = 3600
                if not isinstance(remove_after_upload, bool):
                    remove_after_upload = False

                _s3_uploader = S3LogUploader(
                    log_dir=logs_directory,
                    upload_interval=upload_interval,
                    remove_after_upload=remove_after_upload,
                )
                _s3_uploader.start()
                logger.info("S3 log upload service started")

            except Exception as e:
                logger.warning(f"Could not start S3 log uploader: {e}")

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


def stop_s3_uploader() -> None:
    """
    Stop the S3 log uploader service gracefully.

    Should be called during application shutdown to ensure
    any pending uploads complete properly.
    """
    global _s3_uploader
    if _s3_uploader:
        _s3_uploader.stop()
        _s3_uploader = None


def upload_current_logs() -> None:
    """
    Manually trigger upload of completed log files to S3.

    Useful for testing or forcing immediate upload of logs.
    Only uploads files from previous days to avoid interfering
    with active log files.
    """
    if _s3_uploader:
        _s3_uploader._upload_completed_logs()
    else:
        logger = get_logger(__name__)
        logger.warning("S3 uploader not initialized")


def upload_current_day_log(config: Config) -> None:
    """
    Upload the current day's log file to S3.

    This function specifically uploads today's log file, which is useful
    at the end of a pipeline run to ensure the current session's logs
    are archived alongside generated files.
    """
    from datetime import datetime
    from pathlib import Path

    logger = get_logger(__name__)

    try:
        # Get S3 storage instance
        from the_data_packet.utils.s3 import S3Storage

        s3_storage = S3Storage()

        # Find today's log file
        config = get_config()
        log_dir = Path(getattr(config, "log_dir", "output/logs"))

        if not log_dir.exists():
            logger.warning("Log directory does not exist")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"the-data-packet-{today}.jsonl"

        if not log_file.exists():
            logger.warning(f"Today's log file not found: {log_file}")
            return

        # Upload to S3 with structured path
        timestamp = datetime.now().strftime("%Y-%m-%d")
        s3_key = (
            f"{config.show_name.lower().replace(' ', '-')}/{timestamp}/{log_file.name}"
        )

        result = s3_storage.upload_file(
            local_path=log_file, s3_key=s3_key, content_type="application/x-ndjson"
        )

        if result.success:
            logger.info(
                f"Uploaded current day's log file to S3: {result.s3_url}")
        else:
            logger.error(
                f"Failed to upload current day's log file: {result.error_message}"
            )

        # Upload to Grafana Loki if configured
        if (
            config.grafana_loki_url
            and config.grafana_loki_username
            and config.grafana_loki_password
        ):
            try:
                from the_data_packet.utils.loki import upload_logs_to_loki

                # Construct the full Loki push URL
                loki_push_url = f"{config.grafana_loki_url}/loki/api/v1/push"

                count = upload_logs_to_loki(
                    file_path=log_file,
                    url=loki_push_url,
                    user=config.grafana_loki_username,
                    api_key=config.grafana_loki_password,
                )
                logger.info(
                    f"Successfully uploaded {count} log entries to Loki")
            except Exception as e:
                logger.error(f"Error uploading logs to Loki: {e}")
        else:
            logger.debug(
                "Loki configuration not complete, skipping log upload")

    except Exception as e:
        logger.error(f"Error uploading current day's log file: {e}")
