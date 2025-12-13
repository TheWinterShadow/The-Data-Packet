"""Tests for models article module."""

import unittest
from datetime import datetime

from the_data_packet.models.article import ArticleData


class TestArticleData(unittest.TestCase):
    """Test cases for ArticleData class."""

    def test_initialization_with_all_fields(self):
        """Test ArticleData initialization with all fields."""
        article = ArticleData(
            title="Test Title",
            author="Test Author",
            content="Test content",
            url="https://example.com",
            category="test",
        )

        self.assertEqual(article.title, "Test Title")
        self.assertEqual(article.author, "Test Author")
        self.assertEqual(article.content, "Test content")
        self.assertEqual(article.url, "https://example.com")
        self.assertEqual(article.category, "test")

    def test_initialization_with_defaults(self):
        """Test ArticleData initialization with default values."""
        article = ArticleData()

        self.assertEqual(article.title, "")
        self.assertEqual(article.author, "")
        self.assertEqual(article.content, "")
        self.assertEqual(article.url, "")
        self.assertEqual(article.category, "")
        self.assertIsInstance(article.published_date, datetime)

    def test_to_dict(self):
        """Test converting ArticleData to dictionary."""
        article = ArticleData(
            title="Test Title",
            author="Test Author",
            content="Test content",
            url="https://example.com",
            category="security"
        )

        article_dict = article.to_dict()

        self.assertIsInstance(article_dict, dict)
        self.assertEqual(article_dict['title'], "Test Title")
        self.assertEqual(article_dict['author'], "Test Author")
        self.assertEqual(article_dict['content'], "Test content")
        self.assertEqual(article_dict['url'], "https://example.com")
        self.assertEqual(article_dict['category'], "security")

    def test_str_representation(self):
        """Test string representation of ArticleData."""
        article = ArticleData(
            title="Test Title",
            author="Test Author",
            url="https://example.com"
        )

        str_repr = str(article)
        self.assertIn("Test Title", str_repr)

    def test_equality(self):
        """Test equality comparison between ArticleData objects."""
        article1 = ArticleData(
            title="Same Title",
            author="Same Author",
            url="https://same-url.com"
        )

        article2 = ArticleData(
            title="Same Title",
            author="Same Author",
            url="https://same-url.com"
        )

        article3 = ArticleData(
            title="Different Title",
            author="Same Author",
            url="https://same-url.com"
        )

        self.assertEqual(article1, article2)
        self.assertNotEqual(article1, article3)


if __name__ == '__main__':
    unittest.main()
