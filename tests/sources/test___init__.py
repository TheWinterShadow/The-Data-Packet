"""Unit tests for sources.__init__.py module."""

import unittest

from the_data_packet.sources import (
    Article,
    ArticleSource,
    TechCrunchSource,
    WiredSource,
)


class TestSourcesInit(unittest.TestCase):
    """Test cases for sources module initialization."""

    def test_all_imports_available(self):
        """Test that all expected classes are importable."""
        # Test that classes exist and are importable
        self.assertIsNotNone(ArticleSource)
        self.assertIsNotNone(Article)
        self.assertIsNotNone(TechCrunchSource)
        self.assertIsNotNone(WiredSource)

    def test_classes_are_callable(self):
        """Test that imported classes are actually classes."""
        self.assertTrue(callable(Article))
        # ArticleSource is abstract, so just check it's a class
        self.assertTrue(hasattr(ArticleSource, "__abstractmethods__"))
        self.assertTrue(callable(TechCrunchSource))
        self.assertTrue(callable(WiredSource))

    def test_module_all_attribute(self):
        """Test that __all__ attribute contains expected items."""
        import the_data_packet.sources as sources_module

        expected_items = ["ArticleSource", "Article", "TechCrunchSource", "WiredSource"]

        self.assertTrue(hasattr(sources_module, "__all__"))
        for item in expected_items:
            self.assertIn(item, sources_module.__all__)

    def test_article_source_inheritance(self):
        """Test that source classes inherit from ArticleSource."""
        self.assertTrue(issubclass(TechCrunchSource, ArticleSource))
        self.assertTrue(issubclass(WiredSource, ArticleSource))


if __name__ == "__main__":
    unittest.main()
