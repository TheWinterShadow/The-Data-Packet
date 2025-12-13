"""Tests for scrapers package __init__.py module."""

import unittest


class TestScrapersInit(unittest.TestCase):
    """Test cases for scrapers package __init__.py module."""

    def test_scrapers_module_imports(self):
        """Test that scrapers module classes are importable."""
        from the_data_packet.scrapers import WiredArticleScraper

        self.assertIsNotNone(WiredArticleScraper)

    def test_scrapers_module_all_exports(self):
        """Test scrapers module __all__ exports."""
        import the_data_packet.scrapers as scrapers_module

        if hasattr(scrapers_module, '__all__'):
            expected_exports = ['WiredArticleScraper']
            for export in expected_exports:
                self.assertIn(export, scrapers_module.__all__)


if __name__ == '__main__':
    unittest.main()
