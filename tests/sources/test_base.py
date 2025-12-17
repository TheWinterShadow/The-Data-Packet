"""Unit tests for sources.base module."""

import unittest
from unittest.mock import Mock

from the_data_packet.core.exceptions import ValidationError
from the_data_packet.sources.base import Article, ArticleSource


class TestArticle(unittest.TestCase):
    """Test cases for Article dataclass."""

    def test_article_creation_minimal(self):
        """Test Article creation with minimal required fields."""
        article = Article(title="Test Title", content="Test content for the article")

        self.assertEqual(article.title, "Test Title")
        self.assertEqual(article.content, "Test content for the article")
        self.assertIsNone(article.author)
        self.assertIsNone(article.url)
        self.assertIsNone(article.category)
        self.assertIsNone(article.source)

    def test_article_creation_with_all_fields(self):
        """Test Article creation with all fields."""
        article = Article(
            title="Complete Article",
            content="This is complete article content with enough text to be valid.",
            author="John Doe",
            url="https://example.com/article",
            category="technology",
            source="example",
        )

        self.assertEqual(article.title, "Complete Article")
        self.assertEqual(article.author, "John Doe")
        self.assertEqual(article.url, "https://example.com/article")
        self.assertEqual(article.category, "technology")
        self.assertEqual(article.source, "example")

    def test_is_valid_with_valid_article(self):
        """Test is_valid returns True for valid articles."""
        article = Article(
            title="Valid Article",
            content="This is a sufficiently long article content that should pass the validation requirements for the article.",
        )

        self.assertTrue(article.is_valid())

    def test_is_valid_with_empty_title(self):
        """Test is_valid returns False for empty title."""
        article = Article(
            title="",
            content="This is a sufficiently long article content that should pass the validation requirements for the article.",
        )

        self.assertFalse(article.is_valid())

    def test_is_valid_with_empty_content(self):
        """Test is_valid returns False for empty content."""
        article = Article(title="Valid Title", content="")

        self.assertFalse(article.is_valid())

    def test_is_valid_with_short_content(self):
        """Test is_valid returns False for very short content."""
        article = Article(
            title="Valid Title", content="Short"  # Less than 100 characters
        )

        self.assertFalse(article.is_valid())

    def test_is_valid_with_whitespace_only_content(self):
        """Test is_valid handles whitespace-only content correctly."""
        article = Article(title="Valid Title", content="   \n\t   ")  # Only whitespace

        self.assertFalse(article.is_valid())

    def test_is_valid_content_length_boundary(self):
        """Test is_valid with content at the 100-character boundary."""
        # Exactly 100 characters of content (after stripping)
        content_100 = "a" * 100
        article_100 = Article(title="Title", content=content_100)
        self.assertFalse(article_100.is_valid())  # Must be > 100

        # 101 characters of content (after stripping)
        content_101 = "a" * 101
        article_101 = Article(title="Title", content=content_101)
        self.assertTrue(article_101.is_valid())

    def test_to_dict(self):
        """Test conversion to dictionary."""
        article = Article(
            title="Test Article",
            content="Test content for the article",
            author="Test Author",
            url="https://example.com",
            category="tech",
            source="test_source",
        )

        expected_dict = {
            "title": "Test Article",
            "content": "Test content for the article",
            "author": "Test Author",
            "url": "https://example.com",
            "category": "tech",
            "source": "test_source",
        }

        self.assertEqual(article.to_dict(), expected_dict)

    def test_to_dict_with_none_values(self):
        """Test to_dict with None values."""
        article = Article(title="Test Article", content="Test content")

        expected_dict = {
            "title": "Test Article",
            "content": "Test content",
            "author": None,
            "url": None,
            "category": None,
            "source": None,
        }

        self.assertEqual(article.to_dict(), expected_dict)


class ConcreteArticleSource(ArticleSource):
    """Concrete implementation of ArticleSource for testing."""

    def __init__(self, name="test", categories=None):
        self._name = name
        self._categories = categories or ["tech", "science"]

    @property
    def name(self):
        return self._name

    @property
    def supported_categories(self):
        return self._categories

    def get_latest_article(self, category):
        return Article(
            title=f"Latest {category} article",
            content=f"This is the latest article from the {category} category with enough content to be valid.",
            category=category,
            source=self._name,
        )

    def get_multiple_articles(self, category, count):
        return [
            Article(
                title=f"{category} article {i}",
                content=f"This is article {i} from the {category} category with enough content to be valid.",
                category=category,
                source=self._name,
            )
            for i in range(1, count + 1)
        ]


class TestArticleSource(unittest.TestCase):
    """Test cases for ArticleSource abstract base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.source = ConcreteArticleSource()

    def test_abstract_properties_implemented(self):
        """Test that abstract properties are implemented in concrete class."""
        self.assertEqual(self.source.name, "test")
        self.assertEqual(self.source.supported_categories, ["tech", "science"])

    def test_abstract_methods_implemented(self):
        """Test that abstract methods are implemented in concrete class."""
        # Test get_latest_article
        article = self.source.get_latest_article("tech")
        self.assertIsInstance(article, Article)
        self.assertEqual(article.title, "Latest tech article")
        self.assertEqual(article.category, "tech")

        # Test get_multiple_articles
        articles = self.source.get_multiple_articles("science", 3)
        self.assertEqual(len(articles), 3)
        self.assertEqual(articles[0].title, "science article 1")
        self.assertEqual(articles[1].title, "science article 2")

    def test_validate_category_valid(self):
        """Test validate_category with valid category."""
        # Should not raise any exception
        self.source.validate_category("tech")
        self.source.validate_category("science")

    def test_validate_category_invalid(self):
        """Test validate_category with invalid category."""
        with self.assertRaises(ValidationError) as cm:
            self.source.validate_category("invalid")

        error_message = str(cm.exception)
        self.assertIn("Category 'invalid' not supported", error_message)
        self.assertIn("test", error_message)  # Source name
        self.assertIn("tech, science", error_message)  # Supported categories

    def test_validate_category_case_sensitive(self):
        """Test that category validation is case sensitive."""
        with self.assertRaises(ValidationError):
            self.source.validate_category("TECH")  # Wrong case

        with self.assertRaises(ValidationError):
            self.source.validate_category("Tech")  # Wrong case

    def test_cannot_instantiate_abstract_class(self):
        """Test that ArticleSource cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            ArticleSource()

    def test_subclass_must_implement_abstract_methods(self):
        """Test that subclass must implement all abstract methods."""

        class IncompleteSource(ArticleSource):
            @property
            def name(self):
                return "incomplete"

            # Missing other required methods

        with self.assertRaises(TypeError):
            IncompleteSource()

    def test_custom_source_implementation(self):
        """Test custom source with different categories."""
        custom_source = ConcreteArticleSource(
            name="custom", categories=["ai", "security", "blockchain"]
        )

        self.assertEqual(custom_source.name, "custom")
        self.assertEqual(
            custom_source.supported_categories, ["ai", "security", "blockchain"]
        )

        # Valid categories
        custom_source.validate_category("ai")
        custom_source.validate_category("security")

        # Invalid category
        with self.assertRaises(ValidationError):
            custom_source.validate_category("tech")


if __name__ == "__main__":
    unittest.main()
