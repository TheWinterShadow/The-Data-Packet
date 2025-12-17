"""Unit tests for core.exceptions module."""

import unittest

from the_data_packet.core.exceptions import (
    AIGenerationError,
    AudioGenerationError,
    ConfigurationError,
    NetworkError,
    ScrapingError,
    TheDataPacketError,
    ValidationError,
)


class TestExceptions(unittest.TestCase):
    """Test cases for exception hierarchy."""

    def test_base_exception_inheritance(self):
        """Test that TheDataPacketError inherits from Exception."""
        self.assertTrue(issubclass(TheDataPacketError, Exception))

        # Test instantiation
        exc = TheDataPacketError("Base error")
        self.assertIsInstance(exc, Exception)
        self.assertEqual(str(exc), "Base error")

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inheritance and behavior."""
        self.assertTrue(issubclass(ConfigurationError, TheDataPacketError))
        self.assertTrue(issubclass(ConfigurationError, Exception))

        exc = ConfigurationError("Config error")
        self.assertIsInstance(exc, ConfigurationError)
        self.assertIsInstance(exc, TheDataPacketError)
        self.assertEqual(str(exc), "Config error")

    def test_network_error_inheritance(self):
        """Test NetworkError inheritance and behavior."""
        self.assertTrue(issubclass(NetworkError, TheDataPacketError))
        self.assertTrue(issubclass(NetworkError, Exception))

        exc = NetworkError("Network error")
        self.assertIsInstance(exc, NetworkError)
        self.assertIsInstance(exc, TheDataPacketError)
        self.assertEqual(str(exc), "Network error")

    def test_scraping_error_inheritance(self):
        """Test ScrapingError inheritance and behavior."""
        self.assertTrue(issubclass(ScrapingError, TheDataPacketError))
        self.assertTrue(issubclass(ScrapingError, Exception))

        exc = ScrapingError("Scraping error")
        self.assertIsInstance(exc, ScrapingError)
        self.assertIsInstance(exc, TheDataPacketError)
        self.assertEqual(str(exc), "Scraping error")

    def test_ai_generation_error_inheritance(self):
        """Test AIGenerationError inheritance and behavior."""
        self.assertTrue(issubclass(AIGenerationError, TheDataPacketError))
        self.assertTrue(issubclass(AIGenerationError, Exception))

        exc = AIGenerationError("AI error")
        self.assertIsInstance(exc, AIGenerationError)
        self.assertIsInstance(exc, TheDataPacketError)
        self.assertEqual(str(exc), "AI error")

    def test_audio_generation_error_inheritance(self):
        """Test AudioGenerationError inheritance and behavior."""
        self.assertTrue(issubclass(AudioGenerationError, TheDataPacketError))
        self.assertTrue(issubclass(AudioGenerationError, Exception))

        exc = AudioGenerationError("Audio error")
        self.assertIsInstance(exc, AudioGenerationError)
        self.assertIsInstance(exc, TheDataPacketError)
        self.assertEqual(str(exc), "Audio error")

    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance and behavior."""
        self.assertTrue(issubclass(ValidationError, TheDataPacketError))
        self.assertTrue(issubclass(ValidationError, Exception))

        exc = ValidationError("Validation error")
        self.assertIsInstance(exc, ValidationError)
        self.assertIsInstance(exc, TheDataPacketError)
        self.assertEqual(str(exc), "Validation error")

    def test_exception_catching_hierarchy(self):
        """Test that exceptions can be caught by parent classes."""
        # Test that specific exceptions can be caught by base class
        try:
            raise ConfigurationError("Test config error")
        except TheDataPacketError as e:
            self.assertIsInstance(e, ConfigurationError)
            self.assertEqual(str(e), "Test config error")
        else:
            self.fail("ConfigurationError should be caught by TheDataPacketError")

        try:
            raise NetworkError("Test network error")
        except TheDataPacketError as e:
            self.assertIsInstance(e, NetworkError)
        else:
            self.fail("NetworkError should be caught by TheDataPacketError")

    def test_exception_with_no_message(self):
        """Test exceptions without error messages."""
        exceptions = [
            TheDataPacketError(),
            ConfigurationError(),
            NetworkError(),
            ScrapingError(),
            AIGenerationError(),
            AudioGenerationError(),
            ValidationError(),
        ]

        for exc in exceptions:
            self.assertIsInstance(exc, Exception)
            # Should not raise when converted to string
            str(exc)

    def test_exception_with_complex_messages(self):
        """Test exceptions with complex error messages."""
        # Test with formatted strings
        error_msg = (
            "Failed to process article: 'Test Article' with error: Connection timeout"
        )
        exc = ScrapingError(error_msg)
        self.assertEqual(str(exc), error_msg)

        # Test with multiple arguments (should work with *args)
        try:
            exc = ConfigurationError("Missing key:", "ANTHROPIC_API_KEY")
            # Note: Multiple args create a tuple representation
            self.assertIn("Missing key", str(exc))
        except TypeError:
            # Some exception implementations may not support multiple args
            pass

    def test_exception_repr(self):
        """Test exception string representation."""
        exc = AIGenerationError("Test AI error")
        repr_str = repr(exc)

        self.assertIn("AIGenerationError", repr_str)
        self.assertIn("Test AI error", repr_str)

    def test_all_exceptions_defined(self):
        """Test that all expected exception classes are defined."""
        expected_exceptions = [
            "TheDataPacketError",
            "ConfigurationError",
            "NetworkError",
            "ScrapingError",
            "AIGenerationError",
            "AudioGenerationError",
            "ValidationError",
        ]

        import the_data_packet.core.exceptions as exc_module

        for exc_name in expected_exceptions:
            self.assertTrue(hasattr(exc_module, exc_name))
            exc_class = getattr(exc_module, exc_name)
            self.assertTrue(issubclass(exc_class, Exception))


if __name__ == "__main__":
    unittest.main()
