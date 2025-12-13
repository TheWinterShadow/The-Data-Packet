"""Tests for rss_client module."""

import unittest
from unittest.mock import Mock, patch, MagicMock

from the_data_packet.clients.rss_client import RSSClient


class TestRSSClient(unittest.TestCase):
    """Test cases for RSSClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = RSSClient()

    def test_initialization(self):
        """Test RSSClient initialization."""
        self.assertIsNone(self.client.session)
        self.assertTrue(hasattr(self.client, "FEED_URLS"))
        self.assertIn("security", self.client.FEED_URLS)
        self.assertIn("guide", self.client.FEED_URLS)

    def test_feed_urls_are_correct(self):
        """Test that feed URLs are correctly defined."""
        expected_urls = {
            "security": "https://www.wired.com/feed/category/security/latest/rss",
            "guide": "https://www.wired.com/feed/category/gear/latest/rss",
        }

        for category, expected_url in expected_urls.items():
            self.assertEqual(self.client.FEED_URLS[category], expected_url)

    @patch('feedparser.parse')
    def test_fetch_feed_success(self, mock_feedparser):
        """Test successful feed fetching."""
        # Mock feedparser response
        mock_feed = Mock()
        mock_feed.status = 200
        mock_entry = Mock()
        mock_entry.title = "Test Article"
        mock_entry.link = "https://example.com/article"
        mock_entry.published = "Mon, 01 Jan 2024 12:00:00 GMT"
        mock_entry.summary = "Article summary"
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        result = self.client.fetch_feed("security")

        self.assertEqual(result, mock_feed)
        mock_feedparser.assert_called_once_with(
            self.client.FEED_URLS["security"])

    @patch('feedparser.parse')
    def test_fetch_feed_invalid_category(self, mock_feedparser):
        """Test fetching feed with invalid category."""
        with self.assertRaises(ValueError) as cm:
            self.client.fetch_feed("invalid_category")

        self.assertIn("Invalid category", str(cm.exception))
        mock_feedparser.assert_not_called()

    @patch('feedparser.parse')
    def test_fetch_feed_error(self, mock_feedparser):
        """Test feed fetching handles errors."""
        mock_feed = Mock()
        mock_feed.status = 404
        mock_feed.entries = []
        mock_feedparser.return_value = mock_feed

        result = self.client.fetch_feed("security")

        self.assertEqual(result.status, 404)

    @patch('feedparser.parse')
    def test_get_latest_articles(self, mock_feedparser):
        """Test getting latest articles."""
        # Mock feedparser response
        mock_feed = Mock()
        mock_feed.status = 200
        mock_entries = []

        for i in range(5):
            mock_entry = Mock()
            mock_entry.title = f"Article {i+1}"
            mock_entry.link = f"https://example.com/article{i+1}"
            mock_entry.published = "Mon, 01 Jan 2024 12:00:00 GMT"
            mock_entry.summary = f"Summary {i+1}"
            mock_entries.append(mock_entry)

        mock_feed.entries = mock_entries
        mock_feedparser.return_value = mock_feed

        articles = self.client.get_latest_articles("security", count=3)

        self.assertEqual(len(articles), 3)
        self.assertEqual(articles[0].title, "Article 1")
        self.assertEqual(articles[1].title, "Article 2")
        self.assertEqual(articles[2].title, "Article 3")

    @patch('feedparser.parse')
    def test_get_latest_articles_default_count(self, mock_feedparser):
        """Test getting latest articles with default count."""
        mock_feed = Mock()
        mock_feed.status = 200
        mock_entry = Mock()
        mock_entry.title = "Test Article"
        mock_entry.link = "https://example.com/article"
        mock_entry.published = "Mon, 01 Jan 2024 12:00:00 GMT"
        mock_entry.summary = "Article summary"
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        articles = self.client.get_latest_articles("security")

        self.assertEqual(len(articles), 1)

    @patch('feedparser.parse')
    def test_get_latest_articles_empty_feed(self, mock_feedparser):
        """Test getting articles from empty feed."""
        mock_feed = Mock()
        mock_feed.status = 200
        mock_feed.entries = []
        mock_feedparser.return_value = mock_feed

        articles = self.client.get_latest_articles("security")

        self.assertEqual(len(articles), 0)

    def test_get_available_categories(self):
        """Test getting available categories."""
        categories = self.client.get_available_categories()

        self.assertIn("security", categories)
        self.assertIn("guide", categories)
        self.assertEqual(len(categories), 2)

    def test_validate_category_valid(self):
        """Test category validation with valid category."""
        # Should not raise exception
        self.client._validate_category("security")
        self.client._validate_category("guide")

    def test_validate_category_invalid(self):
        """Test category validation with invalid category."""
        with self.assertRaises(ValueError) as cm:
            self.client._validate_category("invalid")

        self.assertIn("Invalid category", str(cm.exception))

    @patch('feedparser.parse')
    def test_parse_feed_entry(self, mock_feedparser):
        """Test parsing individual feed entry."""
        mock_entry = Mock()
        mock_entry.title = "Test Article Title"
        mock_entry.link = "https://wired.com/article"
        mock_entry.published = "Mon, 01 Jan 2024 12:00:00 GMT"
        mock_entry.summary = "Article summary content"
        mock_entry.author = "Test Author"

        parsed = self.client._parse_feed_entry(mock_entry, "security")

        self.assertEqual(parsed.title, "Test Article Title")
        self.assertEqual(parsed.url, "https://wired.com/article")
        self.assertEqual(parsed.category, "security")

    def test_parse_feed_entry_missing_fields(self):
        """Test parsing feed entry with missing fields."""
        mock_entry = Mock()
        mock_entry.title = "Test Article"
        # Missing other required fields
        del mock_entry.link
        del mock_entry.published
        del mock_entry.summary

        # Should handle missing fields gracefully
        parsed = self.client._parse_feed_entry(mock_entry, "security")

        self.assertEqual(parsed.title, "Test Article")
        self.assertEqual(parsed.category, "security")


if __name__ == '__main__':
    unittest.main()
