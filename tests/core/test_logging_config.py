"""Tests for core logging_config module."""

import unittest
from unittest.mock import patch, MagicMock
import logging

from the_data_packet.core.logging_config import get_logger, setup_logging


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


if __name__ == '__main__':
    unittest.main()
