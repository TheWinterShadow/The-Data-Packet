"""TechCrunch.com article source implementation.

This module implements article collection from TechCrunch.com using RSS feeds and
web scraping. TechCrunch provides RSS feeds for different categories that contain
recent article URLs, which are then scraped for full content.

Features:
    - RSS feed-based article discovery
    - Multiple category support (artificial-intelligence, security)
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
    - ai: Artificial intelligence and machine learning articles
    - security: Security and cybersecurity articles

Rate Limiting:
    - Respectful delays between requests
    - Connection reuse via HTTP session
    - Proper User-Agent identification

Example Usage:
    source = TechCrunchSource()

    # Get latest AI article
    article = source.get_latest_article("ai")

    # Get multiple security articles
    articles = source.get_multiple_articles("security", count=3)

    # Check supported categories
    if "ai" in source.supported_categories:
        ai_articles = source.get_multiple_articles("ai", count=5)
"""

import re
import time
from typing import List, Optional

import feedparser
from bs4 import BeautifulSoup

from the_data_packet.core.exceptions import NetworkError, ScrapingError
from the_data_packet.core.logging import get_logger
from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.utils.http import HTTPClient

logger = get_logger(__name__)


class TechCrunchSource(ArticleSource):
    """Article source for TechCrunch.com."""

    def __init__(self) -> None:
        """Initialize TechCrunch source."""
        self.http_client = HTTPClient()
        logger.info("Initialized TechCrunch source")

    # RSS feed URLs for different categories
    RSS_FEEDS = {
        "ai": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "security": "https://techcrunch.com/category/security/feed/",
    }

    # Content patterns to skip during extraction
    SKIP_PATTERNS = [
        "subscribe to techcrunch",
        "most popular",
        "related articles",
        "advertisement",
        "get techcrunch",
        "sign up",
        "newsletter",
        "techcrunch+",
        "techcrunch disrupt",
        "more techcrunch",
        "follow us",
        "share this article",
    ]

    @property
    def name(self) -> str:
        """Source name identifier."""
        return "techcrunch"

    @property
    def supported_categories(self) -> List[str]:
        """List of supported categories."""
        return list(self.RSS_FEEDS.keys())

    def get_latest_article(self, category: str) -> Article:
        """Get the latest article from a category."""
        self.validate_category(category)

        logger.info(f"Fetching latest {category} article from TechCrunch")

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

        if count < 1:
            raise ScrapingError("Count must be at least 1")

        logger.info(f"Fetching {count} {category} articles from TechCrunch")

        try:
            # Get multiple URLs from RSS
            urls = self._get_urls_from_rss(category, count)

            articles = []
            for i, url in enumerate(urls):
                try:
                    # Add delay between requests to be respectful
                    if i > 0:
                        time.sleep(1)

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
            if isinstance(e, (ScrapingError, NetworkError)):
                raise
            raise ScrapingError(f"Failed to get articles from {category}: {e}")

    def _get_latest_url_from_rss(self, category: str) -> str:
        """Get the latest article URL from RSS feed."""
        rss_url = self.RSS_FEEDS[category]

        try:
            logger.debug(f"Fetching RSS feed: {rss_url}")
            response = self.http_client.get(rss_url)
            response.raise_for_status()

            # Parse RSS feed
            feed = feedparser.parse(response.text)

            if not feed.entries:
                raise ScrapingError(f"No articles found in RSS feed: {rss_url}")

            # Get latest article URL
            latest_entry = feed.entries[0]
            if not hasattr(latest_entry, "link"):
                raise ScrapingError(f"RSS entry missing link: {latest_entry}")

            return str(latest_entry.link)

        except Exception as e:
            if isinstance(e, ScrapingError):
                raise
            raise NetworkError(f"Failed to fetch RSS feed {rss_url}: {e}")

    def _get_urls_from_rss(self, category: str, count: int) -> List[str]:
        """Get multiple article URLs from RSS feed."""
        rss_url = self.RSS_FEEDS[category]

        try:
            logger.debug(f"Fetching RSS feed: {rss_url}")
            response = self.http_client.get(rss_url)
            response.raise_for_status()

            # Parse RSS feed
            feed = feedparser.parse(response.text)

            if not feed.entries:
                raise ScrapingError(f"No articles found in RSS feed: {rss_url}")

            # Extract URLs up to requested count
            urls = []
            for entry in feed.entries[:count]:
                if hasattr(entry, "link"):
                    urls.append(entry.link)

            if not urls:
                raise ScrapingError(f"No valid URLs found in RSS feed: {rss_url}")

            return urls

        except Exception as e:
            if isinstance(e, ScrapingError):
                raise
            raise NetworkError(f"Failed to fetch RSS feed {rss_url}: {e}")

    def _extract_article(self, url: str, category: str) -> Article:
        """Extract article content from a TechCrunch URL."""
        try:
            logger.debug(f"Extracting article: {url}")
            response = self.http_client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title = self._extract_title(soup)
            if not title:
                raise ScrapingError(f"No title found for article: {url}")

            # Extract author
            author = self._extract_author(soup)

            # Extract content
            content = self._extract_content(soup)
            if not content:
                raise ScrapingError(f"No content found for article: {url}")

            # Clean content
            content = self._clean_content(content)

            return Article(
                title=title,
                content=content,
                author=author,
                url=url,
                category=category,
                source=self.name,
            )

        except Exception as e:
            if isinstance(e, (ScrapingError, NetworkError)):
                raise
            raise ScrapingError(f"Failed to extract article {url}: {e}")

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title from HTML."""
        # Try multiple selectors for title
        title_selectors = [
            'h1[data-module="ArticleTitle"]',
            "h1.article__title",
            "h1",
            '[data-module="ArticleTitle"]',
            ".post-title",
            ".entry-title",
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title:
                    return title

        # Fallback to page title
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
            # Remove common TechCrunch suffixes
            title = re.sub(r"\s*\|\s*TechCrunch.*$", "", title)
            return title

        return None

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author from HTML."""
        # Try multiple selectors for author
        author_selectors = [
            '[data-module="ArticleByline"] a',
            ".byline a",
            ".author a",
            ".post-author a",
            '[rel="author"]',
            ".article-author a",
        ]

        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text().strip()
                if author:
                    return author

        return None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content from HTML."""
        # Try multiple selectors for content
        content_selectors = [
            '[data-module="ArticleBody"]',
            ".article-content",
            ".post-content",
            ".entry-content",
            ".article__content",
            "div.article-entry",
        ]

        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for unwanted in content_elem.select(
                    "script, style, .advertisement, .ad, .promo"
                ):
                    unwanted.decompose()

                content = content_elem.get_text(separator=" ", strip=True)
                if content and len(content.strip()) > 100:
                    return content

        # Fallback: try to get all paragraphs
        paragraphs = soup.select("p")
        if paragraphs:
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and not self._should_skip_content(text):
                    content_parts.append(text)

            content = " ".join(content_parts)
            if len(content.strip()) > 100:
                return content

        return None

    def _clean_content(self, content: str) -> str:
        """Clean extracted content."""
        if not content:
            return ""

        # Remove multiple whitespace
        content = re.sub(r"\s+", " ", content)

        # Remove content that matches skip patterns
        lines = content.split(". ")
        cleaned_lines = []

        for line in lines:
            if not self._should_skip_content(line):
                cleaned_lines.append(line)

        return ". ".join(cleaned_lines).strip()

    def _should_skip_content(self, text: str) -> bool:
        """Check if content should be skipped based on patterns."""
        text_lower = text.lower()

        # Skip if matches any skip pattern
        for pattern in self.SKIP_PATTERNS:
            if pattern in text_lower:
                return True

        # Skip if too short
        if len(text.strip()) < 10:
            return True

        return False
