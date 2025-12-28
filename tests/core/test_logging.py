"""Unit tests for core.logging module."""

import json
import logging
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from the_data_packet.core.logging import (
    JSONLHandler,
    S3LogUploader,
    get_logger,
    setup_logging,
    upload_current_logs,
)


class TestLogging(unittest.TestCase):
    """Test cases for logging configuration."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original logging config to restore later
        self.original_level = logging.root.level
        self.original_handlers = logging.root.handlers.copy()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original logging configuration
        logging.root.setLevel(self.original_level)
        logging.root.handlers = self.original_handlers

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test.module")

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test.module")

    def test_get_logger_with_module_name(self):
        """Test get_logger with __name__ pattern."""
        logger = get_logger(__name__)

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, __name__)

    def test_get_logger_hierarchy(self):
        """Test that logger names follow hierarchy."""
        parent_logger = get_logger("the_data_packet")
        child_logger = get_logger("the_data_packet.core")

        self.assertIsInstance(parent_logger, logging.Logger)
        self.assertIsInstance(child_logger, logging.Logger)
        self.assertEqual(parent_logger.name, "the_data_packet")
        self.assertEqual(child_logger.name, "the_data_packet.core")

    def test_setup_logging_default_level(self):
        """Test setup_logging with default log level from config."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.log_level = "INFO"
            mock_get_config.return_value = mock_config

            setup_logging()

            # Check that root logger level is set
            self.assertEqual(logging.root.level, logging.INFO)

    def test_setup_logging_with_override(self):
        """Test setup_logging with explicit log level override."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.log_level = "INFO"
            mock_get_config.return_value = mock_config

            setup_logging("DEBUG")

            # Check that override level is used
            self.assertEqual(logging.root.level, logging.DEBUG)

    def test_setup_logging_case_insensitive(self):
        """Test that log level is case insensitive."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.log_level = "INFO"
            mock_get_config.return_value = mock_config

            # Test lowercase
            setup_logging("debug")
            self.assertEqual(logging.root.level, logging.DEBUG)

            # Test mixed case
            setup_logging("WaRnInG")
            self.assertEqual(logging.root.level, logging.WARNING)

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid log level defaults to INFO."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.log_level = "INFO"
            mock_get_config.return_value = mock_config

            setup_logging("INVALID_LEVEL")

            # Should default to INFO level
            self.assertEqual(logging.root.level, logging.INFO)

    def test_third_party_logger_noise_reduction(self):
        """Test that third-party loggers are set to WARNING level."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.log_level = "DEBUG"
            mock_get_config.return_value = mock_config

            setup_logging()

            # Check that third-party loggers are set to WARNING
            third_party_loggers = [
                "requests",
                "urllib3",
                "boto3",
                "botocore",
                "anthropic",
                "google",
                "feedparser",
            ]

            for logger_name in third_party_loggers:
                logger = logging.getLogger(logger_name)
                self.assertEqual(logger.level, logging.WARNING)

    def test_logging_format_configuration(self):
        """Test that logging format is configured correctly."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.log_level = "INFO"
            mock_get_config.return_value = mock_config

            with patch("logging.basicConfig") as mock_basic_config:
                setup_logging()

                mock_basic_config.assert_called_once()
                call_kwargs = mock_basic_config.call_args[1]

                # Check that format includes expected components
                format_str = call_kwargs["format"]
                self.assertIn("%(asctime)s", format_str)
                self.assertIn("%(name)s", format_str)
                self.assertIn("%(levelname)s", format_str)
                self.assertIn("%(message)s", format_str)

                # Check other configuration
                self.assertEqual(call_kwargs["level"], logging.INFO)
                self.assertIn("force", call_kwargs)
                self.assertTrue(call_kwargs["force"])

    def test_logging_multiple_setup_calls(self):
        """Test that multiple setup_logging calls work correctly."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.log_level = "INFO"
            mock_get_config.return_value = mock_config

            # First setup
            setup_logging("DEBUG")
            self.assertEqual(logging.root.level, logging.DEBUG)

            # Second setup should override
            setup_logging("ERROR")
            self.assertEqual(logging.root.level, logging.ERROR)

    def test_logger_functionality(self):
        """Test that logger can actually log messages."""
        logger = get_logger("test.logger")

        # Test that logger methods exist and are callable
        self.assertTrue(hasattr(logger, "debug"))
        self.assertTrue(hasattr(logger, "info"))
        self.assertTrue(hasattr(logger, "warning"))
        self.assertTrue(hasattr(logger, "error"))
        self.assertTrue(hasattr(logger, "critical"))

        self.assertTrue(callable(logger.debug))
        self.assertTrue(callable(logger.info))
        self.assertTrue(callable(logger.warning))
        self.assertTrue(callable(logger.error))
        self.assertTrue(callable(logger.critical))


class TestJSONLHandler(unittest.TestCase):
    """Test cases for JSONLHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"

    def tearDown(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_jsonl_handler_init(self):
        """Test JSONLHandler initialization."""
        handler = JSONLHandler(str(self.log_dir))
        self.assertEqual(handler.log_dir, self.log_dir)

    def test_jsonl_handler_creates_log_directory(self):
        """Test that JSONLHandler creates log directory."""
        log_dir = self.log_dir / "test"
        self.assertFalse(log_dir.exists())

        # Creating handler should create the log directory
        handler = JSONLHandler(str(log_dir))
        self.assertTrue(log_dir.exists())
        self.assertIsInstance(handler, JSONLHandler)

    def test_jsonl_handler_generates_log_file_path(self):
        """Test log file path generation."""
        handler = JSONLHandler(str(self.log_dir))

        # Create a log record to trigger file creation
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record to create the log file
        handler.emit(record)

        # Check that log file was created with correct naming pattern
        today = datetime.now().strftime("%Y-%m-%d")
        expected_file = handler.log_dir / f"the-data-packet-{today}.jsonl"
        self.assertTrue(expected_file.exists())

    def test_jsonl_handler_emit_creates_log_entry(self):
        """Test that emit creates proper JSON log entry."""
        handler = JSONLHandler(str(self.log_dir))

        # Create a log record
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record
        handler.emit(record)

        # Check that log file was created and contains expected data
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = handler.log_dir / f"the-data-packet-{today}.jsonl"
        self.assertTrue(log_file.exists())

        with open(log_file, "r") as f:
            log_line = f.read().strip()
            log_data = json.loads(log_line)

        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["logger"], "test.logger")
        self.assertIn("timestamp", log_data)

    def test_jsonl_handler_with_extra_fields(self):
        """Test JSONLHandler with extra fields in log record."""
        handler = JSONLHandler(str(self.log_dir))

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.user_id = "123"
        record.request_id = "abc-def"
        record.custom_data = {"key": "value"}

        handler.emit(record)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = handler.log_dir / f"the-data-packet-{today}.jsonl"
        with open(log_file, "r") as f:
            log_data = json.loads(f.read().strip())

        self.assertEqual(log_data["user_id"], "123")
        self.assertEqual(log_data["request_id"], "abc-def")
        self.assertEqual(log_data["custom_data"], {"key": "value"})

    def test_jsonl_handler_with_non_serializable_extra_fields(self):
        """Test JSONLHandler with non-JSON-serializable extra fields."""
        handler = JSONLHandler(str(self.log_dir))

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add non-serializable field
        record.non_serializable = set([1, 2, 3])

        handler.emit(record)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = handler.log_dir / f"the-data-packet-{today}.jsonl"
        with open(log_file, "r") as f:
            log_data = json.loads(f.read().strip())

        # Should convert to string
        self.assertIn("non_serializable", log_data)
        self.assertIsInstance(log_data["non_serializable"], str)

    def test_jsonl_handler_error_handling(self):
        """Test JSONLHandler error handling."""
        # Create a handler with a valid temp directory first

        temp_dir = tempfile.mkdtemp()
        handler = JSONLHandler(temp_dir)

        # Make the directory read-only to simulate permission error
        try:
            os.chmod(temp_dir, 0o444)

            record = logging.LogRecord(
                name="test.logger",
                level=logging.INFO,
                pathname="/test/path.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Should not raise exception, should call handleError instead
            with patch.object(handler, "handleError") as mock_handle_error:
                handler.emit(record)
                mock_handle_error.assert_called_once()
        finally:
            # Restore permissions and clean up
            os.chmod(temp_dir, 0o755)
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class TestS3LogUploader(unittest.TestCase):
    """Test cases for S3LogUploader."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_s3_log_uploader_init(self):
        """Test S3LogUploader initialization."""
        uploader = S3LogUploader(
            log_dir=str(self.log_dir), upload_interval=60, remove_after_upload=True
        )

        self.assertEqual(uploader.log_dir, self.log_dir)
        self.assertEqual(uploader.upload_interval, 60)
        self.assertTrue(uploader.remove_after_upload)
        self.assertIsNotNone(uploader._stop_event)
        self.assertIsNone(uploader._thread)

    def test_s3_log_uploader_start_stop(self):
        """Test starting and stopping S3LogUploader."""
        uploader = S3LogUploader(log_dir=str(self.log_dir))

        # Test that start creates a thread
        uploader.start()
        self.assertIsNotNone(uploader._thread)

        # Test that stop sets the stop event
        uploader.stop()
        self.assertTrue(uploader._stop_event.is_set())

    def test_s3_log_uploader_get_s3_storage_success(self):
        """Test successful S3 storage initialization."""
        uploader = S3LogUploader(log_dir=str(self.log_dir))

        with patch("the_data_packet.utils.s3.S3Storage") as mock_s3_class:
            mock_s3_instance = Mock()
            mock_s3_class.return_value = mock_s3_instance

            storage = uploader._get_s3_storage()

            self.assertEqual(storage, mock_s3_instance)
            self.assertEqual(uploader._s3_storage, mock_s3_instance)

    def test_s3_log_uploader_get_s3_storage_failure(self):
        """Test S3 storage initialization failure."""
        uploader = S3LogUploader(log_dir=str(self.log_dir))

        with patch("the_data_packet.utils.s3.S3Storage") as mock_s3_class:
            mock_s3_class.side_effect = Exception("S3 not configured")

            storage = uploader._get_s3_storage()

            self.assertIsNone(storage)

    @patch("the_data_packet.core.logging.logging.getLogger")
    def test_upload_current_day_logs_success(self, mock_get_logger):
        """Test successful upload of current day logs."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch("the_data_packet.core.logging._s3_uploader") as mock_s3_uploader:
            # Test when S3 uploader is available
            upload_current_logs()
            mock_s3_uploader._upload_completed_logs.assert_called_once()

        # Test when S3 uploader is None
        with patch("the_data_packet.core.logging._s3_uploader", None):
            upload_current_logs()
            mock_get_logger.assert_called()

    def test_upload_current_day_logs_no_config(self):
        """Test upload when Loki is not configured."""
        with patch("the_data_packet.core.logging.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.grafana_loki_url = None
            mock_get_config.return_value = mock_config

            with patch("the_data_packet.utils.loki.upload_logs_to_loki") as mock_upload:
                upload_current_logs()

                mock_upload.assert_not_called()


if __name__ == "__main__":
    unittest.main()
