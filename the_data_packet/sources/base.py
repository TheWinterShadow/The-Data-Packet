"""Base classes for article sources.

This module defines the core data structures and interfaces for collecting
articles from various news sources. It provides a standardized way to
represent articles and implement source-specific collection logic.

The design supports:
- Multiple news sources with different scraping strategies
- Consistent article representation across sources
- Validation of article content quality
- Category-based article filtering
- Extensible source implementation

Architecture:
    Article: Data class representing a single news article
    ArticleSource: Abstract base class for implementing news sources

Current Sources:
    - WiredSource: Wired.com articles via RSS feeds
    - TechCrunchSource: TechCrunch.com articles via RSS feeds

Future Sources (extensible):
    - ArsTechnicaSource
    - HackerNewsSource
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Article:
    """Represents a single news article from any source.

    This data class provides a standardized representation of news articles
    regardless of their source. It includes validation methods to ensure
    articles have sufficient content for podcast generation.

    Attributes:
        title: Article headline/title. Required for all articles.
        content: Full article text content. Required and must be substantial.
        author: Article author name. Optional but recommended.
        url: Original article URL. Optional but useful for debugging.
        category: Article category (e.g., 'security', 'guide'). Optional.
        source: Source identifier (e.g., 'wired'). Optional but recommended.

    Content Requirements:
        - Title must be non-empty
        - Content must be at least 100 characters after stripping whitespace
        - Content should be clean text without HTML tags or navigation elements

    Example:
        article = Article(
            title="New Security Vulnerability Discovered",
            content="A critical security flaw has been found...",
            author="Jane Smith",
            url="https://example.com/article",
            category="security",
            source="wired"
        )

        if article.is_valid():
            # Process article for podcast generation
            pass
    """

    title: str
    content: str
    author: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if article has sufficient content for podcast generation.

        Validates that the article has:
        - Non-empty title
        - Non-empty content
        - Content length of at least 100 characters (after stripping)

        Returns:
            True if article meets minimum content requirements

        Example:
            if not article.is_valid():
                logger.warning(f"Skipping invalid article: {article.title}")
                continue
        """
        return bool(self.title and self.content and len(self.content.strip()) > 100)

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert article to dictionary representation.

        Returns:
            Dictionary with all article fields

        Example:
            article_data = article.to_dict()
            json.dump(article_data, file)
        """
        return {
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "url": self.url,
            "category": self.category,
            "source": self.source,
        }


class ArticleSource(ABC):
    """Abstract base class for implementing news article sources.

    This class defines the interface that all article sources must implement.
    It provides a consistent way to collect articles from different news
    websites while handling source-specific details in subclasses.

    Each source implementation should:
    - Define supported categories
    - Implement RSS feed or web scraping logic
    - Handle rate limiting and error recovery
    - Clean and validate article content
    - Return standardized Article objects

    Subclasses must implement:
        name: Property returning source identifier
        supported_categories: Property returning list of valid categories
        get_latest_article(): Method to get single latest article
        get_multiple_articles(): Method to get multiple articles

    Example Implementation:
        class ExampleSource(ArticleSource):
            @property
            def name(self) -> str:
                return "example"

            @property
            def supported_categories(self) -> List[str]:
                return ["tech", "science"]

            def get_latest_article(self, category: str) -> Article:
                # Implementation specific logic
                pass

    Usage:
        source = WiredSource()
        if "security" in source.supported_categories:
            article = source.get_latest_article("security")
            articles = source.get_multiple_articles("security", count=5)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Source name identifier.

        Returns a unique string identifier for this source.
        Used in configuration, logging, and file naming.

        Returns:
            Source identifier (e.g., "wired", "techcrunch")
        """
        pass

    @property
    @abstractmethod
    def supported_categories(self) -> List[str]:
        """List of supported article categories for this source.

        Returns the categories this source can collect articles from.
        Categories should match the source's RSS feeds or section structure.

        Returns:
            List of category strings (e.g., ["security", "guide", "business"])
        """
        pass

    @abstractmethod
    def get_latest_article(self, category: str) -> Article:
        """Get the latest article from a specific category.

        Args:
            category: Category to fetch from (must be in supported_categories)

        Returns:
            Latest Article instance from the category

        Raises:
            ScrapingError: If article collection fails
            ValidationError: If category is not supported
            NetworkError: If network request fails

        Example:
            try:
                article = source.get_latest_article("security")
                logger.info(f"Retrieved: {article.title}")
            except ValidationError:
                logger.error(f"Category 'invalid' not supported")
        """
        pass

    @abstractmethod
    def get_multiple_articles(self, category: str, count: int) -> List[Article]:
        """Get multiple articles from a specific category.

        Args:
            category: Category to fetch from (must be in supported_categories)
            count: Maximum number of articles to return

        Returns:
            List of Article instances (may be fewer than count if unavailable)

        Raises:
            ScrapingError: If article collection fails
            ValidationError: If category is not supported or count is invalid
            NetworkError: If network request fails

        Example:
            articles = source.get_multiple_articles("guide", count=3)
            valid_articles = [a for a in articles if a.is_valid()]
        """
        pass

    def validate_category(self, category: str) -> None:
        """Validate if a category is supported by this source.

        Args:
            category: Category to validate

        Raises:
            ValidationError: If category is not supported

        Example:
            source.validate_category("security")  # OK
            source.validate_category("invalid")   # Raises ValidationError
        """
        from ..core.exceptions import ValidationError

        if category not in self.supported_categories:
            raise ValidationError(
                f"Category '{category}' not supported by {self.name}. "
                f"Supported categories: {', '.join(self.supported_categories)}"
            )
