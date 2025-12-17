"""Unit tests for sources.techcrunch module."""

import unittest
from unittest.mock import Mock, patch

from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.sources.techcrunch import TechCrunchSource


class TestTechCrunchSource(unittest.TestCase):
    """Test cases for TechCrunchSource class."""

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
        self.assertIn("security", categories)
        # TechCrunch typically supports these categories
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
        from the_data_packet.core.exceptions import ValidationError

        with self.assertRaises(ValidationError) as cm:
            self.source.validate_category("unsupported_category")

        error_message = str(cm.exception)
        self.assertIn("unsupported_category", error_message)
        self.assertIn("techcrunch", error_message)

    @patch.object(TechCrunchSource, "_extract_article")
    @patch.object(TechCrunchSource, "_get_latest_url_from_rss")
    def test_get_latest_article_structure(self, mock_get_url, mock_extract):
        """Test get_latest_article method structure (mocked)."""
        mock_get_url.return_value = "https://techcrunch.com/test"
        mock_extract.return_value = Article(
            title="Test TechCrunch Article",
            content="This is test content with sufficient length to meet requirements for validation and processing. The content must be longer than 100 characters to pass the validation checks in the Article.is_valid() method. This should now be sufficient length.",
            url="https://techcrunch.com/test",
            author="Test Author",
            category="ai",
            source="techcrunch",
        )

        if "ai" in self.source.supported_categories:
            article = self.source.get_latest_article("ai")
            self.assertIsInstance(article, Article)
            self.assertEqual(article.source, "techcrunch")
            self.assertEqual(article.category, "ai")

    @patch.object(TechCrunchSource, "_extract_article")
    @patch.object(TechCrunchSource, "_get_urls_from_rss")
    def test_get_multiple_articles_structure(self, mock_get_urls, mock_extract):
        """Test get_multiple_articles method structure (mocked)."""
        mock_get_urls.return_value = [
            "https://techcrunch.com/test1",
            "https://techcrunch.com/test2",
        ]
        mock_extract.side_effect = [
            Article(
                title="TechCrunch Article 1",
                content="Content for article 1 with sufficient character length to be considered valid for processing and validation checks.",
                url="https://techcrunch.com/test1",
                author="Test Author",
                category="ai",
                source="techcrunch",
            ),
            Article(
                title="TechCrunch Article 2",
                content="Content for article 2 with sufficient character length to be considered valid for processing and validation checks.",
                url="https://techcrunch.com/test2",
                author="Test Author",
                category="ai",
                source="techcrunch",
            ),
        ]

        if "ai" in self.source.supported_categories:
            articles = self.source.get_multiple_articles("ai", 3)
            self.assertIsInstance(articles, list)
            # Should not exceed requested count
            self.assertLessEqual(len(articles), 3)

            for article in articles:
                self.assertIsInstance(article, Article)
                self.assertEqual(article.source, "techcrunch")

            for article in articles:
                self.assertIsInstance(article, Article)
                self.assertEqual(article.source, "techcrunch")

    def test_source_initialization(self):
        """Test that source can be initialized without errors."""
        # This tests that __init__ works and doesn't raise exceptions
        source = TechCrunchSource()
        self.assertIsNotNone(source)
        self.assertIsInstance(source, TechCrunchSource)

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


if __name__ == "__main__":
    unittest.main()
