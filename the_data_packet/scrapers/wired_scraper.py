"""Main scraper class for Wired.com articles."""

import logging
from typing import Any, Dict, List, Optional

from the_data_packet.clients import HTTPClient, RSSClient
from the_data_packet.extractors import WiredContentExtractor
from the_data_packet.models import ArticleData

logger = logging.getLogger(__name__)


class WiredArticleScraper:
    """Main scraper for extracting articles from Wired.com."""

    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        """
        Initialize the Wired article scraper.

        Args:
            timeout: HTTP request timeout in seconds
            user_agent: Custom User-Agent string for HTTP requests
        """
        self.rss_client = RSSClient()
        self.http_client = HTTPClient(timeout=timeout, user_agent=user_agent)
        self.extractor = WiredContentExtractor()

        logger.info("Initialized WiredArticleScraper")

    def get_latest_article(self, category: str) -> ArticleData:
        """
        Get the latest article from a specific category.

        Args:
            category: Category to fetch from ('security' or 'guide')

        Returns:
            ArticleData object with extracted article information

        Raises:
            ValueError: If category is not supported
            RuntimeError: If scraping fails
        """
        logger.info(f"Fetching latest {category} article")

        try:
            # Get the latest article URL from RSS feed
            url = self.rss_client.get_latest_article_url(category)

            # Fetch and parse the article page
            soup = self.http_client.get_page(url)

            # Extract article data
            article_data = self.extractor.extract(soup, url=url)
            article_data.category = category

            if not article_data.is_valid():
                raise RuntimeError("Extracted article data is invalid")

            logger.info(
                f"Successfully scraped latest {category} article: "
                f"'{article_data.title}'"
            )
            return article_data

        except Exception as e:
            logger.error(f"Error scraping latest {category} article: {e}")
            raise RuntimeError(f"Failed to scrape latest {category} article") from e

    def get_latest_security_article(self) -> ArticleData:
        """Get the latest security article."""
        return self.get_latest_article("security")

    def get_latest_guide_article(self) -> ArticleData:
        """Get the latest guide article."""
        return self.get_latest_article("guide")

    def get_both_latest_articles(self) -> Dict[str, ArticleData]:
        """
        Get both latest security and guide articles.

        Returns:
            Dictionary with 'security' and 'guide' keys containing ArticleData objects
        """
        logger.info("Fetching both latest articles (security and guide)")

        try:
            security_article = self.get_latest_security_article()
            guide_article = self.get_latest_guide_article()

            result = {"security": security_article, "guide": guide_article}

            logger.info("Successfully fetched both latest articles")
            return result

        except Exception as e:
            logger.error(f"Error fetching latest articles: {e}")
            raise RuntimeError("Failed to fetch latest articles") from e

    def get_multiple_articles(self, category: str, limit: int = 5) -> List[ArticleData]:
        """
        Get multiple articles from a specific category.

        Args:
            category: Category to fetch from
            limit: Maximum number of articles to fetch

        Returns:
            List of ArticleData objects
        """
        logger.info(f"Fetching {limit} articles from {category} category")

        try:
            # Get article URLs from RSS feed
            urls = self.rss_client.get_article_urls(category, limit=limit)

            articles = []
            for i, url in enumerate(urls, 1):
                try:
                    logger.info(f"Scraping article {i}/{len(urls)}: {url}")

                    # Fetch and parse the article page
                    soup = self.http_client.get_page(url)

                    # Extract article data
                    article_data = self.extractor.extract(soup, url=url)
                    article_data.category = category

                    if article_data.is_valid():
                        articles.append(article_data)
                        logger.info(f"Successfully scraped: '{article_data.title}'")
                    else:
                        logger.warning(f"Skipping invalid article: {url}")

                except Exception as e:
                    logger.warning(f"Error scraping article {url}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(articles)}/{len(urls)} articles")
            return articles

        except Exception as e:
            logger.error(f"Error fetching multiple {category} articles: {e}")
            raise RuntimeError(f"Failed to fetch {category} articles") from e

    def scrape_article_from_url(
        self, url: str, category: Optional[str] = None
    ) -> ArticleData:
        """
        Scrape a specific article from its URL.

        Args:
            url: The article URL to scrape
            category: Optional category to assign to the article

        Returns:
            ArticleData object with extracted article information
        """
        logger.info(f"Scraping article from URL: {url}")

        try:
            # Fetch and parse the article page
            soup = self.http_client.get_page(url)

            # Extract article data
            article_data = self.extractor.extract(soup, url=url)
            if category:
                article_data.category = category

            if not article_data.is_valid():
                raise RuntimeError("Extracted article data is invalid")

            logger.info(f"Successfully scraped article: '{article_data.title}'")
            return article_data

        except Exception as e:
            logger.error(f"Error scraping article from {url}: {e}")
            raise RuntimeError(f"Failed to scrape article from {url}") from e

    def close(self) -> None:
        """Close HTTP connections and clean up resources."""
        self.http_client.close()
        logger.info("Closed WiredArticleScraper resources")
