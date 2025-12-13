"""
The Data Packet - A Python package for scraping and extracting article data from Wired.com.

This package provides a comprehensive set of tools for:
- Fetching RSS feeds from Wired.com
- Scraping article content from web pages
- Extracting structured data from articles
- Managing HTTP requests and parsing HTML

Main Components:
- WiredArticleScraper: The main scraper class for extracting articles
- ArticleData: Data model for article information
- RSSClient: Client for fetching RSS feed data
- HTTPClient: HTTP client for fetching web pages
- WiredContentExtractor: Extractor for article content

Usage Example:
    >>> from the_data_packet import WiredArticleScraper
    >>> scraper = WiredArticleScraper()
    >>> article = scraper.get_latest_security_article()
    >>> print(article.title)
    >>> scraper.close()
"""

# Configure package-level logging
import logging

from the_data_packet.__about__ import __version__
from the_data_packet.clients import HTTPClient, RSSClient
from the_data_packet.extractors import WiredContentExtractor
from the_data_packet.models import ArticleData

# Import main classes for easy access
from the_data_packet.scrapers import WiredArticleScraper

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Define what gets imported with "from the_data_packet import *"
__all__ = [
    "__version__",
    "WiredArticleScraper",
    "ArticleData",
    "RSSClient",
    "HTTPClient",
    "WiredContentExtractor",
]
