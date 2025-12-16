"""Base classes for article sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Article:
    """Represents an article from any source."""

    title: str
    content: str
    author: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if article has required content."""
        return bool(self.title and self.content and len(self.content.strip()) > 100)

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "url": self.url,
            "category": self.category,
            "source": self.source,
        }


class ArticleSource(ABC):
    """Abstract base class for article sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Source name identifier."""
        pass

    @property
    @abstractmethod
    def supported_categories(self) -> List[str]:
        """List of supported categories for this source."""
        pass

    @abstractmethod
    def get_latest_article(self, category: str) -> Article:
        """
        Get the latest article from a category.

        Args:
            category: Category to fetch from

        Returns:
            Article instance

        Raises:
            ScrapingError: If scraping fails
            ValidationError: If category is not supported
        """
        pass

    @abstractmethod
    def get_multiple_articles(self, category: str, count: int) -> List[Article]:
        """
        Get multiple articles from a category.

        Args:
            category: Category to fetch from
            count: Maximum number of articles to return

        Returns:
            List of Article instances

        Raises:
            ScrapingError: If scraping fails
            ValidationError: If category is not supported
        """
        pass

    def validate_category(self, category: str) -> None:
        """
        Validate if category is supported.

        Args:
            category: Category to validate

        Raises:
            ValidationError: If category is not supported
        """
        from ..core.exceptions import ValidationError

        if category not in self.supported_categories:
            raise ValidationError(
                f"Category '{category}' not supported by {self.name}. "
                f"Supported categories: {', '.join(self.supported_categories)}"
            )
