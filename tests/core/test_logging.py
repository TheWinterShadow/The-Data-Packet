"""Unit tests for core.logging module."""

import logging
import unittest
from unittest.mock import Mock, patch

from the_data_packet.core.logging import get_logger, setup_logging


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


if __name__ == "__main__":
    unittest.main()
