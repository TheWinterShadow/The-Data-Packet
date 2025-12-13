"""Tests for client modules."""

import unittest
from unittest.mock import MagicMock, Mock, patch

import feedparser
import requests
from bs4 import BeautifulSoup

from the_data_packet.clients import HTTPClient, RSSClient


class TestRSSClient(unittest.TestCase):
    """Test cases for the RSSClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = RSSClient()

    def test_initialization(self):
        """Test RSSClient initialization."""
        client = RSSClient()
        self.assertIsNone(client.session)
        self.assertTrue(hasattr(client, "FEED_URLS"))
        self.assertIn("security", client.FEED_URLS)
        self.assertIn("guide", client.FEED_URLS)

    def test_feed_urls_are_correct(self):
        """Test that feed URLs are correctly defined."""
        expected_urls = {
            "security": "https://www.wired.com/feed/category/security/latest/rss",
            "guide": "https://www.wired.com/feed/tag/wired-guide/latest/rss",
        }
        self.assertEqual(self.client.FEED_URLS, expected_urls)

    @patch("feedparser.parse")
    def test_get_latest_article_url_success(self, mock_parse):
        """Test successful retrieval of latest article URL."""
        # Mock feedparser response
        mock_feed = Mock()
        mock_feed.entries = [{"link": "https://www.wired.com/story/latest-article/"}]
        mock_parse.return_value = mock_feed

        url = self.client.get_latest_article_url("security")

        self.assertEqual(url, "https://www.wired.com/story/latest-article/")
        mock_parse.assert_called_once_with(self.client.FEED_URLS["security"])

    @patch("feedparser.parse")
    def test_get_latest_article_url_no_entries(self, mock_parse):
        """Test handling of empty RSS feed."""
        # Mock feedparser response with no entries
        mock_feed = Mock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed

        with self.assertRaisesRegex(RuntimeError, "No articles found"):
            self.client.get_latest_article_url("security")

    def test_get_latest_article_url_invalid_category(self):
        """Test handling of invalid category."""
        with self.assertRaisesRegex(ValueError, "Unsupported category"):
            self.client.get_latest_article_url("invalid")

    @patch("feedparser.parse")
    def test_get_latest_article_url_exception(self, mock_parse):
        """Test handling of exceptions during RSS parsing."""
        mock_parse.side_effect = Exception("Network error")

        with self.assertRaisesRegex(RuntimeError, "Failed to fetch RSS feed"):
            self.client.get_latest_article_url("security")

    @patch("feedparser.parse")
    def test_get_article_urls_success(self, mock_parse):
        """Test successful retrieval of multiple article URLs."""
        # Mock feedparser response
        mock_feed = Mock()
        mock_feed.entries = [
            {"link": "https://www.wired.com/story/article-1/"},
            {"link": "https://www.wired.com/story/article-2/"},
            {"link": "https://www.wired.com/story/article-3/"},
        ]
        mock_parse.return_value = mock_feed

        urls = self.client.get_article_urls("security", limit=2)

        self.assertEqual(len(urls), 2)
        self.assertEqual(
            urls,
            [
                "https://www.wired.com/story/article-1/",
                "https://www.wired.com/story/article-2/",
            ],
        )

    @patch("feedparser.parse")
    def test_get_article_urls_with_missing_links(self, mock_parse):
        """Test handling of entries without links."""
        # Mock feedparser response with some entries missing links
        mock_feed = Mock()
        mock_feed.entries = [
            {"link": "https://www.wired.com/story/article-1/"},
            {"title": "Article without link"},  # No link field
            {"link": "https://www.wired.com/story/article-2/"},
        ]
        mock_parse.return_value = mock_feed

        urls = self.client.get_article_urls("security", limit=10)

        self.assertEqual(len(urls), 2)
        self.assertEqual(
            urls,
            [
                "https://www.wired.com/story/article-1/",
                "https://www.wired.com/story/article-2/",
            ],
        )

    @patch("feedparser.parse")
    def test_get_feed_data_success(self, mock_parse):
        """Test successful retrieval of feed data."""
        # Mock feedparser response
        mock_feed = Mock()
        mock_feed.feed.title = "WIRED - Security"
        mock_feed.feed.description = "Latest security articles"
        mock_feed.entries = [{"link": "https://example.com"}]
        mock_parse.return_value = mock_feed

        data = self.client.get_feed_data("security")

        self.assertEqual(data["title"], "WIRED - Security")
        self.assertEqual(data["description"], "Latest security articles")
        self.assertEqual(len(data["entries"]), 1)


class TestHTTPClient(unittest.TestCase):
    """Test cases for the HTTPClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = HTTPClient()

    def test_initialization_default(self):
        """Test HTTPClient initialization with defaults."""
        client = HTTPClient()
        self.assertEqual(client.timeout, 30)
        self.assertIn("User-Agent", client.session.headers)
        self.assertIn("Mozilla", client.session.headers["User-Agent"])

    def test_initialization_custom_params(self):
        """Test HTTPClient initialization with custom parameters."""
        custom_ua = "Custom User Agent"
        client = HTTPClient(timeout=60, user_agent=custom_ua)

        self.assertEqual(client.timeout, 60)
        self.assertEqual(client.session.headers["User-Agent"], custom_ua)

    @patch("requests.Session.get")
    def test_get_page_success(self, mock_get):
        """Test successful page retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

    @patch("requests.Session.get")
    def test_get_page_success(self, mock_get):
        """Test successful page retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        soup = self.client.get_page("https://example.com")

        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.find("body").get_text(), "Test content")
        mock_get.assert_called_once_with("https://example.com", timeout=30)

    @patch("requests.Session.get")
    def test_get_page_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        # Mock response that raises HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        with self.assertRaisesRegex(RuntimeError, "Failed to fetch"):
            self.client.get_page("https://example.com")

    @patch("requests.Session.get")
    def test_get_page_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        with self.assertRaisesRegex(RuntimeError, "Failed to fetch"):
            self.client.get_page("https://example.com")

    @patch("requests.Session.get")
    def test_get_raw_content_success(self, mock_get):
        """Test successful raw content retrieval."""
        mock_response = Mock()
        mock_response.text = "<html>Raw content</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        content = self.client.get_raw_content("https://example.com")

        self.assertEqual(content, "<html>Raw content</html>")
        mock_get.assert_called_once_with("https://example.com", timeout=30)

    @patch("requests.Session.get")
    def test_get_raw_content_exception(self, mock_get):
        """Test handling of exceptions during raw content retrieval."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        with self.assertRaisesRegex(RuntimeError, "Failed to fetch"):
            self.client.get_raw_content("https://example.com")

    def test_close(self):
        """Test closing the HTTP session."""
        # Mock the session to verify close is called
        self.client.session = Mock()

        self.client.close()

        self.client.session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
