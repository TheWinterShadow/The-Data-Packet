"""Simple unit tests for sources.techcrunch module."""

import unittest
from unittest.mock import Mock, patch

from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.sources.techcrunch import TechCrunchSource


class TestTechCrunchSourceSimple(unittest.TestCase):
    """Simple test cases for TechCrunchSource class."""

    def setUp(self):
        """Set up test fixtures."""
        self.source = TechCrunchSource()

    def test_inheritance(self):
        """Test that TechCrunchSource inherits from ArticleSource."""
        self.assertIsInstance(self.source, ArticleSource)
        self.assertTrue(issubclass(TechCrunchSource, ArticleSource))

    def test_name_property(self):
        """Test the name property."""
        self.assertEqual(self.source.name, "techcrunch")

    def test_supported_categories_property(self):
        """Test the supported_categories property."""
        categories = self.source.supported_categories
        self.assertIsInstance(categories, list)
        self.assertIn("ai", categories)

    def test_validate_category_supported(self):
        """Test validate_category with supported categories."""
        for category in self.source.supported_categories:
            # Should not raise any exception
            self.source.validate_category(category)

    @patch.object(TechCrunchSource, "_extract_article")
    @patch.object(TechCrunchSource, "_get_latest_url_from_rss")
    def test_get_latest_article_mocked(self, mock_get_url, mock_extract):
        """Test get_latest_article method with mocking."""
        mock_get_url.return_value = "https://techcrunch.com/test"
        mock_extract.return_value = Article(
            title="Test TechCrunch Article",
            content="This is test content with sufficient length to meet the minimum requirements for article validation and processing.",
            url="https://techcrunch.com/test",
            category="ai",
            source="techcrunch",
        )

        article = self.source.get_latest_article("ai")
        self.assertIsInstance(article, Article)
        self.assertEqual(article.source, "techcrunch")


if __name__ == "__main__":
    unittest.main()
