"""Simple unit tests for sources.wired module."""

import unittest
from unittest.mock import MagicMock, patch

from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.sources.wired import WiredSource


class TestWiredSourceSimple(unittest.TestCase):
    """Simple test cases for WiredSource class."""

    def setUp(self):
        """Set up test fixtures."""
        self.source = WiredSource()

    def test_inheritance(self):
        """Test that WiredSource inherits from ArticleSource."""
        self.assertIsInstance(self.source, ArticleSource)
        self.assertTrue(issubclass(WiredSource, ArticleSource))

    def test_name_property(self):
        """Test the name property."""
        self.assertEqual(self.source.name, "wired")

    def test_supported_categories_property(self):
        """Test the supported_categories property."""
        categories = self.source.supported_categories
        self.assertIsInstance(categories, list)
        self.assertIn("security", categories)

    def test_validate_category_supported(self):
        """Test validate_category with supported categories."""
        for category in self.source.supported_categories:
            # Should not raise any exception
            self.source.validate_category(category)

    @patch.object(WiredSource, "_extract_article")
    @patch.object(WiredSource, "_get_latest_url_from_rss")
    def test_get_latest_article_mocked(
        self, mock_get_url: MagicMock, mock_extract: MagicMock
    ):
        """Test get_latest_article method with mocking."""
        mock_get_url.return_value = "https://wired.com/test"
        mock_extract.return_value = Article(
            title="Test Article",
            content=(
                "This is test content with sufficient length to meet the minimum "
                "requirements for article validation and processing."
            ),
            url="https://wired.com/test",
            category="security",
            source="wired",
        )

        article = self.source.get_latest_article("security")
        self.assertIsInstance(article, Article)
        self.assertEqual(article.source, "wired")


if __name__ == "__main__":
    unittest.main()
