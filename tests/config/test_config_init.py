"""Tests for config package __init__.py module."""

import unittest


class TestConfigInit(unittest.TestCase):
    """Test cases for config package __init__.py module."""

    def test_config_module_imports(self):
        """Test that config module classes are importable."""
        from the_data_packet.config import Settings, ConfigurationError

        self.assertIsNotNone(Settings)
        self.assertIsNotNone(ConfigurationError)

    def test_config_module_all_exports(self):
        """Test config module __all__ exports."""
        import the_data_packet.config as config_module

        if hasattr(config_module, '__all__'):
            expected_exports = ['Settings', 'ConfigurationError']
            for export in expected_exports:
                self.assertIn(export, config_module.__all__)


if __name__ == '__main__':
    unittest.main()
