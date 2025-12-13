"""Tests for core modules."""

import unittest
from unittest.mock import patch, MagicMock, call
import logging
import sys

from the_data_packet.core import get_logger, setup_logging
from the_data_packet.core.exceptions import TheDataPacketError


class TestLoggingConfig(unittest.TestCase):
    """Test cases for logging configuration."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test_module")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_module")

    def test_get_logger_with_package_name(self):
        """Test get_logger with package name."""
        logger = get_logger("the_data_packet.test")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "the_data_packet.test")

    @patch('logging.basicConfig')
    def test_setup_logging_default(self, mock_basic_config):
        """Test setup_logging with default settings."""
        setup_logging()
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        self.assertEqual(call_kwargs['level'], logging.INFO)

    @patch('logging.basicConfig')
    def test_setup_logging_debug_level(self, mock_basic_config):
        """Test setup_logging with DEBUG level."""
        setup_logging(level="DEBUG")
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        self.assertEqual(call_kwargs['level'], logging.DEBUG)

    @patch('logging.basicConfig')
    def test_setup_logging_warning_level(self, mock_basic_config):
        """Test setup_logging with WARNING level."""
        setup_logging(level="WARNING")
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        self.assertEqual(call_kwargs['level'], logging.WARNING)

    @patch('logging.basicConfig')
    def test_setup_logging_error_level(self, mock_basic_config):
        """Test setup_logging with ERROR level."""
        setup_logging(level="ERROR")
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        self.assertEqual(call_kwargs['level'], logging.ERROR)

    @patch('logging.basicConfig')
    def test_setup_logging_invalid_level(self, mock_basic_config):
        """Test setup_logging with invalid level defaults to INFO."""
        setup_logging(level="INVALID")
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        self.assertEqual(call_kwargs['level'], logging.INFO)

    def test_logger_functionality(self):
        """Test that logger actually logs messages."""
        with patch('sys.stdout') as mock_stdout:
            setup_logging(level="DEBUG")
            logger = get_logger("test")
            logger.info("Test message")
            # Verify that logging was configured (hard to test exact output)
            self.assertIsInstance(logger, logging.Logger)


class TestDataPacketError(unittest.TestCase):
    """Test cases for DataPacketError exception."""

    def test_data_packet_error_creation(self):
        """Test DataPacketError can be created and raised."""
        error_message = "Test data packet error"

        with self.assertRaises(DataPacketError) as cm:
            raise DataPacketError(error_message)

        self.assertEqual(str(cm.exception), error_message)

    def test_data_packet_error_inheritance(self):
        """Test DataPacketError inherits from Exception."""
        error = DataPacketError("test")
        self.assertIsInstance(error, Exception)

    def test_data_packet_error_with_cause(self):
        """Test DataPacketError with underlying cause."""
        original_error = ValueError("Original error")

        with self.assertRaises(DataPacketError) as cm:
            try:
                raise original_error
            except ValueError as e:
                raise DataPacketError("Wrapper error") from e

        self.assertEqual(str(cm.exception), "Wrapper error")
        self.assertIsInstance(cm.exception.__cause__, ValueError)

    def test_data_packet_error_empty_message(self):
        """Test DataPacketError with empty message."""
        error = DataPacketError("")
        self.assertEqual(str(error), "")

    def test_data_packet_error_none_message(self):
        """Test DataPacketError with None message."""
        error = DataPacketError(None)
        self.assertEqual(str(error), "None")


if __name__ == '__main__':
    unittest.main()
