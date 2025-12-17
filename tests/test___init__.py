"""Unit tests for __init__.py module."""

import unittest

import the_data_packet
from the_data_packet import (
    AIGenerationError,
    AudioGenerationError,
    AudioGenerator,
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


class TestInit(unittest.TestCase):
    """Test cases for package initialization and exports."""

    def test_version_import(self):
        """Test that version is importable from main package."""
        self.assertTrue(hasattr(the_data_packet, "__version__"))
        self.assertIsInstance(the_data_packet.__version__, str)

    def test_core_imports(self):
        """Test that core components are importable."""
        # Test exception classes
        self.assertTrue(issubclass(TheDataPacketError, Exception))
        self.assertTrue(issubclass(ConfigurationError, TheDataPacketError))
        self.assertTrue(issubclass(NetworkError, TheDataPacketError))
        self.assertTrue(issubclass(ScrapingError, TheDataPacketError))
        self.assertTrue(issubclass(AIGenerationError, TheDataPacketError))
        self.assertTrue(issubclass(AudioGenerationError, TheDataPacketError))
        self.assertTrue(issubclass(ValidationError, TheDataPacketError))

        # Test config system
        self.assertTrue(callable(get_config))
        config = get_config()
        self.assertIsInstance(config, Config)

        # Test logging system
        self.assertTrue(callable(setup_logging))
        self.assertTrue(callable(get_logger))
        logger = get_logger(__name__)
        self.assertIsNotNone(logger)

    def test_generation_imports(self):
        """Test that generation components are importable."""
        # These should be importable without errors
        self.assertTrue(hasattr(the_data_packet, "AudioGenerator"))
        self.assertIsNotNone(AudioGenerator)

    def test_exception_hierarchy(self):
        """Test that exception hierarchy is correctly set up."""
        # Test that all custom exceptions inherit from base
        exceptions = [
            ConfigurationError,
            NetworkError,
            ScrapingError,
            AIGenerationError,
            AudioGenerationError,
            ValidationError,
        ]

        for exc_class in exceptions:
            self.assertTrue(issubclass(exc_class, TheDataPacketError))
            # Test that they can be instantiated
            instance = exc_class("Test message")
            self.assertIsInstance(instance, exc_class)
            self.assertIsInstance(instance, TheDataPacketError)
            self.assertEqual(str(instance), "Test message")

    def test_package_structure(self):
        """Test that expected modules are accessible."""
        # Test that submodules exist
        import the_data_packet.core
        import the_data_packet.generation

        # Note: Not testing sources/utils/workflows as they may have dependencies


if __name__ == "__main__":
    unittest.main()
