"""Tests for package __init__.py module."""

import unittest

import the_data_packet


class TestPackageInit(unittest.TestCase):
    """Test cases for package __init__.py module."""

    def test_package_imports(self):
        """Test that main classes are importable from package root."""
        from the_data_packet import (
            ArticleData,
            HTTPClient,
            RSSClient,
            WiredArticleScraper,
            WiredContentExtractor,
            __version__
        )

        self.assertIsNotNone(ArticleData)
        self.assertIsNotNone(HTTPClient)
        self.assertIsNotNone(RSSClient)
        self.assertIsNotNone(WiredArticleScraper)
        self.assertIsNotNone(WiredContentExtractor)
        self.assertIsNotNone(__version__)

    def test_version_attribute(self):
        """Test that __version__ is available at package level."""
        self.assertTrue(hasattr(the_data_packet, '__version__'))
        self.assertIsInstance(the_data_packet.__version__, str)

    def test_package_name(self):
        """Test package name is correct."""
        self.assertEqual(the_data_packet.__name__, 'the_data_packet')

    def test_all_exports(self):
        """Test that __all__ is defined and contains expected exports."""
        self.assertTrue(hasattr(the_data_packet, '__all__'))
        self.assertIsInstance(the_data_packet.__all__, list)

        expected_exports = [
            'ArticleData',
            'HTTPClient',
            'RSSClient',
            'WiredArticleScraper',
            'WiredContentExtractor',
            '__version__'
        ]

        for export in expected_exports:
            self.assertIn(export, the_data_packet.__all__)


if __name__ == '__main__':
    unittest.main()
