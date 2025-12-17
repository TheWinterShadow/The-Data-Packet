"""Unit tests for core.__init__.py module."""

import unittest

from the_data_packet.core import (
    AIGenerationError,
    AudioGenerationError,
    Config,
    ConfigurationError,
    NetworkError,
    ScrapingError,
    TheDataPacketError,
    ValidationError,
    get_config,
    get_logger,
    setup_logging,
)


class TestCoreInit(unittest.TestCase):
    """Test cases for core module initialization and exports."""

    def test_all_imports_available(self):
        """Test that all expected symbols are importable."""
        # Test exception classes
        self.assertTrue(issubclass(TheDataPacketError, Exception))
        self.assertTrue(issubclass(ConfigurationError, TheDataPacketError))
        self.assertTrue(issubclass(NetworkError, TheDataPacketError))
        self.assertTrue(issubclass(ScrapingError, TheDataPacketError))
        self.assertTrue(issubclass(AIGenerationError, TheDataPacketError))
        self.assertTrue(issubclass(AudioGenerationError, TheDataPacketError))
        self.assertTrue(issubclass(ValidationError, TheDataPacketError))

    def test_config_functions(self):
        """Test that config functions are available."""
        self.assertTrue(callable(get_config))
        config = get_config()
        self.assertIsInstance(config, Config)

    def test_logging_functions(self):
        """Test that logging functions are available."""
        self.assertTrue(callable(setup_logging))
        self.assertTrue(callable(get_logger))

        logger = get_logger(__name__)
        self.assertIsNotNone(logger)

    def test_exception_instantiation(self):
        """Test that exceptions can be instantiated."""
        exceptions = [
            TheDataPacketError,
            ConfigurationError,
            NetworkError,
            ScrapingError,
            AIGenerationError,
            AudioGenerationError,
            ValidationError,
        ]

        for exc_class in exceptions:
            instance = exc_class("Test message")
            self.assertIsInstance(instance, exc_class)
            self.assertEqual(str(instance), "Test message")


if __name__ == "__main__":
    unittest.main()
