"""Wired.com article source implementation.

This module implements article collection from Wired.com using RSS feeds and
web scraping. Wired.com provides RSS feeds for different categories that contain
recent article URLs, which are then scraped for full content.

Features:
    - RSS feed-based article discovery
    - Multiple category support (security, guides, business, science, AI)
    - Robust content extraction with fallback methods
    - Content cleaning and validation
    - Error handling for network issues and malformed content

RSS Feed Strategy:
    1. Fetch category-specific RSS feed
    2. Parse feed to extract article URLs
    3. Scrape individual articles for full content
    4. Clean and validate extracted content
    5. Return standardized Article objects

Content Extraction:
    - Primary: Article body containers and paragraph tags
    - Fallback: Main content areas and text containers
    - Cleaning: Remove navigation, ads, and boilerplate text
    - Validation: Ensure sufficient content length

Supported Categories:
    - security: Security and cybersecurity articles
    - guide: How-to guides and tutorials
    - business: Business and industry news
    - science: Science and technology research
    - ai: Artificial intelligence and machine learning

Rate Limiting:
    - Respectful delays between requests
    - Connection reuse via HTTP session
    - Proper User-Agent identification

Example Usage:
    source = WiredSource()

    # Get latest security article
    article = source.get_latest_article(\"security\")

    # Get multiple guide articles
    articles = source.get_multiple_articles(\"guide\", count=3)

    # Check supported categories
    if \"ai\" in source.supported_categories:
        ai_articles = source.get_multiple_articles(\"ai\", count=5)
"""

import re
from typing import List, Optional

import feedparser
from bs4 import BeautifulSoup

from the_data_packet.core.exceptions import NetworkError, ScrapingError
from the_data_packet.core.logging import get_logger
from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.utils.http import HTTPClient

logger = get_logger(__name__)


class WiredSource(ArticleSource):
    """Article source for Wired.com."""

    def __init__(self) -> None:
        """Initialize Wired source."""
        self.http_client = HTTPClient()
        logger.info("Initialized Wired source")

    # RSS feed URLs for different categories
    RSS_FEEDS = {
        "security": "https://www.wired.com/feed/category/security/latest/rss",
        "science": "https://www.wired.com/feed/category/science/latest/rss",
        "ai": "https://www.wired.com/feed/tag/ai/latest/rss",
    }

    # Content patterns to skip during extraction
    SKIP_PATTERNS = [
        "subscribe to wired",
        "most popular",
        "related stories",
        "advertisement",
        "get wired",
        "sign up",
        "newsletter",
    ]

    @property
    def name(self) -> str:
        """Source name identifier."""
        return "wired"

    @property
    def supported_categories(self) -> List[str]:
        """List of supported categories."""
        return list(self.RSS_FEEDS.keys())

    def get_latest_article(self, category: str) -> Article:
        """Get the latest article from a category."""
        self.validate_category(category)

        logger.info(f"Fetching latest {category} article from Wired")

        try:
            # Get latest article URL from RSS
            url = self._get_latest_url_from_rss(category)

            # Fetch and extract article content
            article = self._extract_article(url, category)

            if not article.is_valid():
                raise ScrapingError("Extracted article is not valid: missing content")

            logger.info(f"Successfully extracted article: {article.title}")
            return article

        except Exception as e:
            if isinstance(e, (ScrapingError, NetworkError)):
                raise
            raise ScrapingError(f"Failed to get latest article from {category}: {e}")

    def get_multiple_articles(self, category: str, count: int) -> List[Article]:
        """Get multiple articles from a category."""
        self.validate_category(category)

        logger.info(f"Fetching {count} {category} articles from Wired")

        try:
            # Get multiple URLs from RSS
            urls = self._get_urls_from_rss(category, count)

            articles = []
            for url in urls:
                try:
                    article = self._extract_article(url, category)
                    if article.is_valid():
                        articles.append(article)
                    else:
                        logger.warning(f"Skipping invalid article: {url}")
                except Exception as e:
                    logger.warning(f"Failed to extract article {url}: {e}")
                    continue

            if not articles:
                raise ScrapingError(f"No valid articles found in {category}")

            logger.info(f"Successfully extracted {len(articles)} articles")
            return articles

        except Exception as e:
            if isinstance(e, ScrapingError):
                raise
            raise ScrapingError(f"Failed to get articles from {category}: {e}")

    def _get_latest_url_from_rss(self, category: str) -> str:
        """Get the latest article URL from RSS feed."""
        urls = self._get_urls_from_rss(category, 1)
        if not urls:
            raise ScrapingError(f"No articles found in RSS feed for {category}")
        return urls[0]

    def _get_urls_from_rss(self, category: str, count: int) -> List[str]:
        """Get article URLs from RSS feed."""
        rss_url = self.RSS_FEEDS[category]

        logger.debug(f"Fetching RSS feed: {rss_url}")

        try:
            # Parse RSS feed
            feed = feedparser.parse(rss_url)

            if not feed.entries:
                raise ScrapingError(f"No entries found in RSS feed for {category}")

            # Extract URLs
            urls = []
            for entry in feed.entries[:count]:
                if hasattr(entry, "link"):
                    urls.append(entry.link)

            if not urls:
                raise ScrapingError(f"No valid URLs found in RSS feed for {category}")

            logger.debug(f"Found {len(urls)} article URLs")
            return urls

        except Exception as e:
            if isinstance(e, ScrapingError):
                raise
            raise NetworkError(f"Failed to fetch RSS feed {rss_url}: {e}")

    def _extract_article(self, url: str, category: str) -> Article:
        """Extract article content from a Wired article page."""
        logger.debug(f"Extracting article: {url}")

        try:
            # Fetch article page
            soup = self._fetch_page(url)

            # Extract article data
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            content = self._extract_content(soup)

            return Article(
                title=title,
                content=content,
                author=author,
                url=url,
                category=category,
                source=self.name,
            )

        except Exception as e:
            if isinstance(e, (NetworkError, ScrapingError)):
                raise
            raise ScrapingError(f"Failed to extract article from {url}: {e}")

    def _fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page."""
        soup = self.http_client.get_soup(url)
        return soup

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title."""
        # Try multiple selectors for title
        selectors = [
            "h1[data-testid='ContentHeaderHed']",
            "h1.ContentHeaderHed",
            "h1.entry-title",
            "h1",
            "title",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                title = element.get_text(strip=True)
                # Clean title
                title = re.sub(r"\s+", " ", title)
                if title and len(title) > 5:  # Basic validation
                    return title

        raise ScrapingError("Could not extract article title")

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author."""
        # Try multiple selectors for author
        selectors = [
            "[data-testid='ContentHeaderAccreditation'] a",
            ".ContentHeaderAccreditation a",
            ".byline a",
            ".author a",
            "[rel='author']",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                author = element.get_text(strip=True)
                author = re.sub(r"\s+", " ", author)
                if author:
                    return author

        return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content."""
        # Try multiple selectors for content
        selectors = [
            "[data-testid='ArticleBodyWrapper']",
            ".ArticleBodyWrapper",
            ".content-body",
            ".entry-content",
            "article",
        ]

        content_element = None
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                content_element = element
                break

        if not content_element:
            raise ScrapingError("Could not find article content")

        # Extract text and clean it
        paragraphs = []
        for p in content_element.find_all(["p", "div"], recursive=True):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out short snippets
                # Skip unwanted content
                text_lower = text.lower()
                if any(pattern in text_lower for pattern in self.SKIP_PATTERNS):
                    continue
                paragraphs.append(text)

        if not paragraphs:
            raise ScrapingError("No content paragraphs found")

        content = "\n\n".join(paragraphs)

        # Final cleaning
        content = re.sub(r"\s+", " ", content)
        content = content.strip()

        if len(content) < 100:
            raise ScrapingError("Article content too short")

        return content
