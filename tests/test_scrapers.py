"""Tests for scraper modules."""

import unittest
from unittest.mock import Mock, patch

from the_data_packet.models import ArticleData
from the_data_packet.scrapers import WiredArticleScraper


class TestWiredArticleScraper(unittest.TestCase):
    """Test cases for the WiredArticleScraper class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample article data
        self.sample_article_data = ArticleData(
            title="Test Article Title",
            author="Test Author",
            content="This is test content for the article.",
            url="https://www.wired.com/story/test-article/",
            category="security",
        )

        # Create mock scraper with mocked dependencies
        self.scraper = WiredArticleScraper()
        self.scraper.rss_client = Mock()
        self.scraper.http_client = Mock()
        self.scraper.extractor = Mock()

        # Configure default mock returns
        self.scraper.rss_client.get_latest_article_url.return_value = (
            "https://www.wired.com/story/latest-article/"
        )
        self.scraper.rss_client.get_article_urls.return_value = [
            "https://www.wired.com/story/article-1/",
            "https://www.wired.com/story/article-2/",
        ]
        self.scraper.http_client.get_page.return_value = Mock()
        self.scraper.extractor.extract.return_value = self.sample_article_data

    def test_initialization_default(self):
        """Test WiredArticleScraper initialization with defaults."""
        scraper = WiredArticleScraper()

        self.assertTrue(hasattr(scraper, "rss_client"))
        self.assertTrue(hasattr(scraper, "http_client"))
        self.assertTrue(hasattr(scraper, "extractor"))

    def test_initialization_custom_params(self):
        """Test WiredArticleScraper initialization with custom parameters."""
        scraper = WiredArticleScraper(timeout=60, user_agent="Custom Agent")

        # Verify that HTTPClient was initialized with custom parameters
        self.assertEqual(scraper.http_client.timeout, 60)

    def test_get_latest_article_success(self):
        """Test successful retrieval of latest article."""
        result = self.scraper.get_latest_article("security")

        self.assertIsInstance(result, ArticleData)
        self.assertEqual(result.category, "security")
        self.assertEqual(result.title, self.sample_article_data.title)

        # Verify method calls
        self.scraper.rss_client.get_latest_article_url.assert_called_once_with(
            "security"
        )
        self.scraper.http_client.get_page.assert_called_once()
        self.scraper.extractor.extract.assert_called_once()

    def test_get_latest_article_invalid_category(self):
        """Test handling of invalid category."""
        self.scraper.rss_client.get_latest_article_url.side_effect = ValueError(
            "Unsupported category"
        )

    def test_get_latest_article_invalid_data(self):
        """Test handling of invalid extracted data."""
        # Mock extractor to return invalid data
        invalid_article = ArticleData()  # No title or content
        self.scraper.extractor.extract.return_value = invalid_article

        with self.assertRaises(RuntimeError) as cm:
            self.scraper.get_latest_article("security")
        self.assertIn("Failed to scrape latest security article", str(cm.exception))

    def test_get_latest_security_article(self):
        """Test shortcut method for security articles."""
        result = self.scraper.get_latest_security_article()

        self.assertEqual(result.category, "security")
        self.scraper.rss_client.get_latest_article_url.assert_called_once_with(
            "security"
        )

    def test_get_latest_guide_article(self):
        """Test shortcut method for guide articles."""
        result = self.scraper.get_latest_guide_article()

        self.assertEqual(result.category, "guide")
        self.scraper.rss_client.get_latest_article_url.assert_called_once_with("guide")

    def test_get_both_latest_articles(self):
        """Test retrieval of both latest articles."""
        # Configure mock to return different data for each call
        security_article = ArticleData(
            title="Security Article", content="Security content"
        )
        guide_article = ArticleData(title="Guide Article", content="Guide content")

        self.scraper.extractor.extract.side_effect = [security_article, guide_article]

        result = self.scraper.get_both_latest_articles()

        self.assertIn("security", result)
        self.assertIn("guide", result)
        self.assertEqual(result["security"].title, "Security Article")
        self.assertEqual(result["guide"].title, "Guide Article")

        # Should be called twice (once for each category)
        self.assertEqual(self.scraper.rss_client.get_latest_article_url.call_count, 2)

    def test_get_multiple_articles_success(self):
        """Test successful retrieval of multiple articles."""
        # Mock RSS client to return multiple URLs
        urls = [
            "https://www.wired.com/story/article-1/",
            "https://www.wired.com/story/article-2/",
        ]
        self.scraper.rss_client.get_article_urls.return_value = urls

        # Mock extractor to return valid articles
        self.scraper.extractor.extract.return_value = self.sample_article_data

        result = self.scraper.get_multiple_articles("security", limit=2)

        self.assertEqual(len(result), 2)
        for article in result:
            self.assertIsInstance(article, ArticleData)
            self.assertEqual(article.category, "security")

        # Verify method calls
        self.scraper.rss_client.get_article_urls.assert_called_once_with(
            "security", limit=2
        )
        self.assertEqual(self.scraper.http_client.get_page.call_count, 2)
        self.assertEqual(self.scraper.extractor.extract.call_count, 2)

    def test_get_multiple_articles_with_failures(self):
        """Test handling of individual article failures in batch processing."""
        # Mock RSS client to return multiple URLs
        urls = [
            "https://www.wired.com/story/article-1/",
            "https://www.wired.com/story/article-2/",
            "https://www.wired.com/story/article-3/",
        ]
        self.scraper.rss_client.get_article_urls.return_value = urls

        # Mock HTTP client to fail on second URL
        def mock_get_page(url):
            if "article-2" in url:
                raise RuntimeError("HTTP Error")
            return Mock()

        self.scraper.http_client.get_page.side_effect = mock_get_page

        # Mock extractor to return valid articles for successful requests
        self.scraper.extractor.extract.return_value = self.sample_article_data

        result = self.scraper.get_multiple_articles("security", limit=3)

        # Should get 2 articles (1st and 3rd), skipping the failed one
        self.assertEqual(len(result), 2)
        for article in result:
            self.assertIsInstance(article, ArticleData)

    def test_get_multiple_articles_with_invalid_data(self):
        """Test handling of invalid article data in batch processing."""
        # Mock RSS client to return URLs
        urls = ["https://www.wired.com/story/article-1/"]
        self.scraper.rss_client.get_article_urls.return_value = urls

        # Mock extractor to return invalid data
        invalid_article = ArticleData()  # No title or content
        self.scraper.extractor.extract.return_value = invalid_article

        result = self.scraper.get_multiple_articles("security", limit=1)

        # Should skip invalid articles
        self.assertEqual(len(result), 0)

    def test_scrape_article_from_url_success(self):
        """Test successful scraping from specific URL."""
        url = "https://www.wired.com/story/specific-article/"
        self.scraper.extractor.extract.return_value = self.sample_article_data

        result = self.scraper.scrape_article_from_url(url, category="custom")

        # URL is set by extractor
        self.assertEqual(result.url, self.sample_article_data.url)
        self.assertEqual(result.category, "custom")

        self.scraper.http_client.get_page.assert_called_once_with(url)
        self.scraper.extractor.extract.assert_called_once()

    def test_scrape_article_from_url_without_category(self):
        """Test scraping from URL without specifying category."""
        url = "https://www.wired.com/story/specific-article/"
        self.scraper.extractor.extract.return_value = self.sample_article_data

        result = self.scraper.scrape_article_from_url(url)

        # Category should remain as set by sample data or None
        self.assertEqual(result.category, self.sample_article_data.category)

    def test_scrape_article_from_url_http_error(self):
        """Test handling of HTTP errors when scraping specific URL."""
        url = "https://www.wired.com/story/nonexistent/"
        self.scraper.http_client.get_page.side_effect = RuntimeError("404 Not Found")

        with self.assertRaises(RuntimeError) as cm:
            self.scraper.scrape_article_from_url(url)
        self.assertIn("Failed to scrape article", str(cm.exception))

    def test_scrape_article_from_url_invalid_data(self):
        """Test handling of invalid extracted data from specific URL."""
        url = "https://www.wired.com/story/invalid-content/"

        # Mock extractor to return invalid data
        invalid_article = ArticleData()
        self.scraper.extractor.extract.return_value = invalid_article

        with self.assertRaises(RuntimeError) as cm:
            self.scraper.scrape_article_from_url(url)
        self.assertIn("invalid", str(cm.exception))

    def test_close(self):
        """Test closing scraper resources."""
        self.scraper.close()

        self.scraper.http_client.close.assert_called_once()

    def test_error_handling_in_get_latest_article(self):
        """Test error propagation in get_latest_article."""
        # Mock RSS client to raise an error
        self.scraper.rss_client.get_latest_article_url.side_effect = RuntimeError(
            "RSS Error"
        )

        with self.assertRaises(RuntimeError) as cm:
            self.scraper.get_latest_article("security")
        self.assertIn("Failed to scrape latest security article", str(cm.exception))

    def test_error_handling_in_get_both_latest_articles(self):
        """Test error handling when one of the articles fails in get_both_latest_articles."""

        # Mock to succeed for security but fail for guide
        def mock_extract(*args, **kwargs):
            if self.scraper.rss_client.get_latest_article_url.call_count == 1:
                return self.sample_article_data  # Success for security
            else:
                raise RuntimeError("Extraction failed")  # Fail for guide

        self.scraper.extractor.extract.side_effect = mock_extract

        with self.assertRaises(RuntimeError) as cm:
            self.scraper.get_both_latest_articles()
        self.assertIn("Failed to fetch latest articles", str(cm.exception))
