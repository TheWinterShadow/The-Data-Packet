"""Tests for extractors package __init__.py module."""

import unittest


class TestExtractorsInit(unittest.TestCase):
    """Test cases for extractors package __init__.py module."""

    def test_extractors_module_imports(self):
        """Test that extractors module classes are importable."""
        from the_data_packet.extractors import WiredContentExtractor

        self.assertIsNotNone(WiredContentExtractor)

    def test_extractors_module_all_exports(self):
        """Test extractors module __all__ exports."""
        import the_data_packet.extractors as extractors_module

        if hasattr(extractors_module, '__all__'):
            expected_exports = ['WiredContentExtractor']
            for export in expected_exports:
                self.assertIn(export, extractors_module.__all__)


if __name__ == '__main__':
    unittest.main()
