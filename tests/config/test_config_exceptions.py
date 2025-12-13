"""Tests for config exceptions module."""

import unittest

from the_data_packet.config.exceptions import ConfigurationError


class TestConfigurationError(unittest.TestCase):
    """Test cases for ConfigurationError exception."""

    def test_configuration_error_creation(self):
        """Test ConfigurationError can be created and raised."""
        error_message = "Test configuration error"

        with self.assertRaises(ConfigurationError) as cm:
            raise ConfigurationError(error_message)

        self.assertEqual(str(cm.exception), error_message)

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from Exception."""
        error = ConfigurationError("test")
        self.assertIsInstance(error, Exception)

    def test_configuration_error_with_cause(self):
        """Test ConfigurationError with underlying cause."""
        original_error = ValueError("Original error")

        with self.assertRaises(ConfigurationError) as cm:
            try:
                raise original_error
            except ValueError as e:
                raise ConfigurationError("Wrapper error") from e

        self.assertEqual(str(cm.exception), "Wrapper error")
        self.assertIsInstance(cm.exception.__cause__, ValueError)


if __name__ == '__main__':
    unittest.main()
