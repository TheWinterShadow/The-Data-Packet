"""RSS feed client for fetching article URLs."""

import logging
from typing import Any, Dict, List

import feedparser

logger = logging.getLogger(__name__)


class RSSClient:
    """Client for fetching RSS feed data from Wired.com."""

    # RSS feed URLs for different categories
    FEED_URLS = {
        "security": "https://www.wired.com/feed/category/security/latest/rss",
        "guide": "https://www.wired.com/feed/tag/wired-guide/latest/rss",
    }

    def __init__(self) -> None:
        """Initialize the RSS client."""
        self.session = None

    def get_latest_article_url(self, category: str) -> str:
        """
        Get the URL of the latest article from a specific category.

        Args:
            category: The category to fetch from ('security' or 'guide')

        Returns:
            The URL of the latest article

        Raises:
            ValueError: If category is not supported
            RuntimeError: If no articles are found
        """
        if category not in self.FEED_URLS:
            raise ValueError(
                f"Unsupported category: {category}. "
                f"Supported categories: {list(self.FEED_URLS.keys())}"
            )

        feed_url = self.FEED_URLS[category]
        logger.info(f"Fetching RSS feed for category: {category}")

        try:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                raise RuntimeError(f"No articles found in {category} feed")

            latest_url: str = feed.entries[0]["link"]
            logger.info(f"Found latest article URL: {latest_url}")
            return latest_url

        except Exception as e:
            logger.error(f"Error fetching RSS feed for {category}: {e}")
            raise RuntimeError(f"Failed to fetch RSS feed: {e}") from e

    def get_article_urls(self, category: str, limit: int = 10) -> List[str]:
        """
        Get multiple article URLs from a specific category.

        Args:
            category: The category to fetch from
            limit: Maximum number of URLs to return

        Returns:
            List of article URLs
        """
        if category not in self.FEED_URLS:
            raise ValueError(f"Unsupported category: {category}")

        feed_url = self.FEED_URLS[category]
        logger.info(f"Fetching {limit} articles from {category} RSS feed")

        try:
            feed = feedparser.parse(feed_url)

            urls = []
            for entry in feed.entries[:limit]:
                if "link" in entry:
                    urls.append(entry["link"])

            logger.info(f"Found {len(urls)} article URLs")
            return urls

        except Exception as e:
            logger.error(f"Error fetching RSS feed for {category}: {e}")
            raise RuntimeError(f"Failed to fetch RSS feed: {e}") from e

    def get_feed_data(self, category: str) -> Dict[str, Any]:
        """
        Get full feed data for a category.

        Args:
            category: The category to fetch from

        Returns:
            Dictionary containing feed metadata and entries
        """
        if category not in self.FEED_URLS:
            raise ValueError(f"Unsupported category: {category}")

        feed_url = self.FEED_URLS[category]

        try:
            feed = feedparser.parse(feed_url)
            return {
                "title": getattr(feed.feed, "title", ""),
                "description": getattr(feed.feed, "description", ""),
                "entries": feed.entries,
            }
        except Exception as e:
            logger.error(f"Error fetching feed data for {category}: {e}")
            raise RuntimeError(f"Failed to fetch feed data: {e}") from e
