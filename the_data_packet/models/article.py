"""Article data model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ArticleData:
    """Represents scraped article data from Wired.com."""

    title: Optional[str] = None
    author: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate and clean data after initialization."""
        if self.title:
            self.title = self.title.strip()
        if self.author:
            self.author = self.author.strip()
        if self.content:
            self.content = self.content.strip()

    def is_valid(self) -> bool:
        """Check if the article data is valid (has title and content)."""
        return bool(self.title and self.content)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "title": self.title,
            "author": self.author,
            "content": self.content,
            "url": self.url,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArticleData":
        """Create ArticleData instance from dictionary."""
        return cls(
            title=data.get("title"),
            author=data.get("author"),
            content=data.get("content"),
            url=data.get("url"),
            category=data.get("category"),
        )
