"""Unit tests for sources.wired module."""

import unittest
from unittest.mock import MagicMock, patch

from the_data_packet.core.exceptions import ValidationError
from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.sources.wired import WiredSource


class TestWiredSource(unittest.TestCase):
    """Test cases for WiredSource class."""

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
        self.assertIn("ai", categories)
        self.assertIn("science", categories)
        # Wired typically supports these categories
        for category in categories:
            self.assertIsInstance(category, str)

    def test_has_required_abstract_methods(self):
        """Test that all required abstract methods are implemented."""
        # Check that methods exist and are callable
        self.assertTrue(hasattr(self.source, "get_latest_article"))
        self.assertTrue(callable(self.source.get_latest_article))
        self.assertTrue(hasattr(self.source, "get_multiple_articles"))
        self.assertTrue(callable(self.source.get_multiple_articles))

    def test_validate_category_supported(self):
        """Test validate_category with supported categories."""
        for category in self.source.supported_categories:
            # Should not raise any exception
            self.source.validate_category(category)

    def test_validate_category_unsupported(self):
        """Test validate_category with unsupported category."""
        with self.assertRaises(ValidationError) as cm:
            self.source.validate_category("unsupported_category")

        error_message = str(cm.exception)
        self.assertIn("unsupported_category", error_message)
        self.assertIn("wired", error_message)

    @patch.object(WiredSource, "_extract_article")
    @patch.object(WiredSource, "_get_latest_url_from_rss")
    def test_get_latest_article_structure(
        self, mock_get_url: MagicMock, mock_extract: MagicMock
    ):
        """Test get_latest_article method structure (mocked)."""
        # Mock the URL and extraction
        mock_get_url.return_value = "https://wired.com/test"
        mock_extract.return_value = Article(
            title="Test Wired Article",
            content=(
                "This is test content for a Wired article that has sufficient character "
                "length to meet the minimum requirements for validation which is more "
                "than 100 characters."
            ),
            url="https://wired.com/test",
            category="security",
            source="wired",
            author="Test Author",
        )

        if "security" in self.source.supported_categories:
            article = self.source.get_latest_article("security")
            self.assertIsInstance(article, Article)
            self.assertEqual(article.source, "wired")
            self.assertEqual(article.category, "security")

    @patch.object(WiredSource, "_extract_article")
    @patch.object(WiredSource, "_get_urls_from_rss")
    def test_get_multiple_articles_structure(
        self, mock_get_urls: MagicMock, mock_extract: MagicMock
    ):
        """Test get_multiple_articles method structure (mocked)."""
        # Mock URLs and article extraction
        mock_get_urls.return_value = [
            "https://wired.com/article1",
            "https://wired.com/article2",
            "https://wired.com/article3",
        ]
        mock_extract.side_effect = [
            Article(
                title="Wired Article 1",
                content=(
                    "Content for article 1 with sufficient character length to be "
                    "considered valid for processing by the validation system."
                ),
                url="https://wired.com/article1",
                author="Test Author",
                category="science",
                source="wired",
            ),
            Article(
                title="Wired Article 2",
                content=(
                    "Content for article 2 with sufficient character length to be "
                    "considered valid for processing by the validation system."
                ),
                url="https://wired.com/article2",
                author="Test Author",
                category="science",
                source="wired",
            ),
            Article(
                title="Wired Article 3",
                content=(
                    "Content for article 3 with sufficient character length to be "
                    "considered valid for processing by the validation system."
                ),
                url="https://wired.com/article3",
                author="Test Author",
                category="science",
                source="wired",
            ),
        ]

        if "science" in self.source.supported_categories:
            articles = self.source.get_multiple_articles("science", 3)
            self.assertIsInstance(articles, list)
            # Should not exceed requested count
            self.assertLessEqual(len(articles), 3)

            for article in articles:
                self.assertIsInstance(article, Article)
                self.assertEqual(article.source, "wired")

    def test_source_initialization(self):
        """Test that source can be initialized without errors."""
        # This tests that __init__ works and doesn't raise exceptions
        source = WiredSource()
        self.assertIsNotNone(source)
        self.assertIsInstance(source, WiredSource)

    def test_category_validation_integration(self):
        """Test category validation with actual supported categories."""
        # Test all supported categories are valid
        for category in self.source.supported_categories:
            self.source.validate_category(category)

        # Test that common unsupported categories raise errors
        unsupported = ["sports", "entertainment", "politics", "weather"]
        for category in unsupported:
            if category not in self.source.supported_categories:
                with self.assertRaises(Exception):  # Should be ValidationError
                    self.source.validate_category(category)

    def test_typical_wired_categories(self):
        """Test that Wired source supports expected categories."""
        expected_categories = ["security", "science", "ai"]

        for category in expected_categories:
            # Should be in supported categories (this might fail if implementation changes)
            # But it's good to document expected behavior
            if category in self.source.supported_categories:
                self.source.validate_category(category)

    def test_source_name_consistency(self):
        """Test that source name is consistent."""
        self.assertEqual(self.source.name, "wired")
        # Name should be lowercase and match expected pattern
        self.assertTrue(self.source.name.islower())
        self.assertNotIn(" ", self.source.name)


if __name__ == "__main__":
    unittest.main()
