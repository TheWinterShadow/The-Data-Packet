"""Fixed unit tests for sources.wired module."""

import unittest
from unittest.mock import Mock, patch

from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.sources.wired import WiredSource


class TestWiredSourceFixed(unittest.TestCase):
    """Fixed test cases for WiredSource class."""

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

    @patch.object(WiredSource, "_extract_article")
    @patch.object(WiredSource, "_get_latest_url_from_rss")
    def test_get_latest_article_mocked(self, mock_get_url, mock_extract):
        """Test get_latest_article method with mocking."""
        mock_get_url.return_value = "https://wired.com/test"
        mock_extract.return_value = Article(
            title="Test Wired Article",
            content="This is test content for a Wired article that has sufficient character length to meet the minimum requirements for validation which is more than 100 characters.",
            url="https://wired.com/test",
            category="security",
            source="wired",
            author="Test Author",
        )

        article = self.source.get_latest_article("security")
        self.assertIsInstance(article, Article)
        self.assertEqual(article.source, "wired")
        self.assertEqual(article.category, "security")

    @patch.object(WiredSource, "_extract_article")
    @patch.object(WiredSource, "_get_urls_from_rss")
    def test_get_multiple_articles_mocked(self, mock_get_urls, mock_extract):
        """Test get_multiple_articles method with mocking."""
        mock_get_urls.return_value = [
            "https://wired.com/article1",
            "https://wired.com/article2",
        ]
        mock_extract.side_effect = [
            Article(
                title="Wired Article 1",
                content="Content for article 1 with sufficient character length to be considered valid for processing by the validation system.",
                url="https://wired.com/article1",
                author="Test Author",
                category="science",
                source="wired",
            ),
            Article(
                title="Wired Article 2",
                content="Content for article 2 with sufficient character length to be considered valid for processing by the validation system.",
                url="https://wired.com/article2",
                author="Test Author",
                category="science",
                source="wired",
            ),
        ]

        articles = self.source.get_multiple_articles("science", 2)
        self.assertIsInstance(articles, list)
        self.assertLessEqual(len(articles), 2)

        for article in articles:
            self.assertIsInstance(article, Article)
            self.assertEqual(article.source, "wired")


if __name__ == "__main__":
    unittest.main()
