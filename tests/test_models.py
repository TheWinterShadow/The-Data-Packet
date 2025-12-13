"""Tests for the ArticleData model."""

import unittest

from the_data_packet.models import ArticleData


class TestArticleData(unittest.TestCase):
    """Test cases for the ArticleData class."""

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

        self.assertIsNone(article.title)
        self.assertIsNone(article.author)
        self.assertIsNone(article.content)
        self.assertIsNone(article.url)
        self.assertIsNone(article.category)

    def test_post_init_strips_whitespace(self):
        """Test that __post_init__ strips whitespace from fields."""
        article = ArticleData(
            title="  Test Title  ", author="  Test Author  ", content="  Test content  "
        )

        self.assertEqual(article.title, "Test Title")
        self.assertEqual(article.author, "Test Author")
        self.assertEqual(article.content, "Test content")

    def test_post_init_handles_none_values(self):
        """Test that __post_init__ handles None values gracefully."""
        article = ArticleData(title=None, author=None, content=None)

        self.assertIsNone(article.title)
        self.assertIsNone(article.author)
        self.assertIsNone(article.content)

    def test_is_valid_with_title_and_content(self):
        """Test is_valid returns True when title and content exist."""
        article = ArticleData(title="Test Title", content="Test content")

        self.assertTrue(article.is_valid())

    def test_is_valid_without_title(self):
        """Test is_valid returns False when title is missing."""
        article = ArticleData(content="Test content")

        self.assertFalse(article.is_valid())

    def test_is_valid_without_content(self):
        """Test is_valid returns False when content is missing."""
        article = ArticleData(title="Test Title")

        self.assertFalse(article.is_valid())

    def test_is_valid_with_empty_strings(self):
        """Test is_valid returns False with empty strings."""
        article = ArticleData(title="", content="")

        self.assertFalse(article.is_valid())

    def test_to_dict(self):
        """Test conversion to dictionary."""
        article = ArticleData(
            title="Test Title",
            author="Test Author",
            content="Test content",
            url="https://example.com",
            category="test",
        )

        expected = {
            "title": "Test Title",
            "author": "Test Author",
            "content": "Test content",
            "url": "https://example.com",
            "category": "test",
        }

        self.assertEqual(article.to_dict(), expected)

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "title": "Test Title",
            "author": "Test Author",
            "content": "Test content",
            "url": "https://example.com",
            "category": "test",
        }

        article = ArticleData.from_dict(data)

        self.assertEqual(article.title, "Test Title")
        self.assertEqual(article.author, "Test Author")
        self.assertEqual(article.content, "Test content")
        self.assertEqual(article.url, "https://example.com")
        self.assertEqual(article.category, "test")

    def test_from_dict_with_missing_fields(self):
        """Test creation from dictionary with missing fields."""
        data = {"title": "Test Title"}

        article = ArticleData.from_dict(data)

        self.assertEqual(article.title, "Test Title")
        self.assertIsNone(article.author)
        self.assertIsNone(article.content)
        self.assertIsNone(article.url)
        self.assertIsNone(article.category)

    def test_from_dict_empty(self):
        """Test creation from empty dictionary."""
        article = ArticleData.from_dict({})

        self.assertIsNone(article.title)
        self.assertIsNone(article.author)
        self.assertIsNone(article.content)
        self.assertIsNone(article.url)
        self.assertIsNone(article.category)


if __name__ == "__main__":
    unittest.main()
