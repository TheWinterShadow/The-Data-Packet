"""Tests for core package __init__.py module."""

import unittest


class TestCoreInit(unittest.TestCase):
    """Test cases for core package __init__.py module."""

    def test_core_module_imports(self):
        """Test that core module functions are importable."""
        from the_data_packet.core import get_logger, setup_logging

        self.assertIsNotNone(get_logger)
        self.assertIsNotNone(setup_logging)

    def test_core_module_all_exports(self):
        """Test core module __all__ exports."""
        import the_data_packet.core as core_module

        if hasattr(core_module, '__all__'):
            expected_exports = ['get_logger', 'setup_logging']
            for export in expected_exports:
                self.assertIn(export, core_module.__all__)


if __name__ == '__main__':
    unittest.main()
