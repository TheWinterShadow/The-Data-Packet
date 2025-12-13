"""Tests for scrapers wired_scraper module."""

import unittest
from unittest.mock import Mock, patch, MagicMock

from the_data_packet.scrapers.wired_scraper import WiredArticleScraper


class TestWiredArticleScraper(unittest.TestCase):
    """Test cases for WiredArticleScraper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = WiredArticleScraper()

    def test_initialization(self):
        """Test WiredArticleScraper initialization."""
        scraper = WiredArticleScraper()
        self.assertIsNotNone(scraper.rss_client)
        self.assertIsNotNone(scraper.content_extractor)

    @patch('the_data_packet.scrapers.wired_scraper.RSSClient')
    @patch('the_data_packet.scrapers.wired_scraper.WiredContentExtractor')
    def test_get_latest_article_success(self, mock_extractor_class, mock_rss_class):
        """Test successful retrieval of latest article."""
        # Mock RSS client
        mock_rss = Mock()
        mock_article_data = Mock()
        mock_article_data.url = "https://wired.com/article"
        mock_rss.get_latest_articles.return_value = [mock_article_data]
        mock_rss_class.return_value = mock_rss

        # Mock content extractor
        mock_extractor = Mock()
        mock_extracted = Mock()
        mock_extracted.title = "Test Article"
        mock_extracted.content = "Test content"
        mock_extractor.extract_from_url.return_value = mock_extracted
        mock_extractor_class.return_value = mock_extractor

        scraper = WiredArticleScraper()
        result = scraper.get_latest_article("security")

        self.assertEqual(result, mock_extracted)
        mock_rss.get_latest_articles.assert_called_once_with("security", 1)
        mock_extractor.extract_from_url.assert_called_once_with(
            "https://wired.com/article")

    @patch('the_data_packet.scrapers.wired_scraper.RSSClient')
    def test_get_latest_article_no_articles(self, mock_rss_class):
        """Test handling when no articles are found."""
        mock_rss = Mock()
        mock_rss.get_latest_articles.return_value = []
        mock_rss_class.return_value = mock_rss

        scraper = WiredArticleScraper()

        with self.assertRaises(ValueError) as cm:
            scraper.get_latest_article("security")

        self.assertIn("No articles found", str(cm.exception))

    @patch('the_data_packet.scrapers.wired_scraper.RSSClient')
    @patch('the_data_packet.scrapers.wired_scraper.WiredContentExtractor')
    def test_get_multiple_articles_success(self, mock_extractor_class, mock_rss_class):
        """Test successful retrieval of multiple articles."""
        # Mock RSS client
        mock_rss = Mock()
        mock_article1 = Mock()
        mock_article1.url = "https://wired.com/article1"
        mock_article2 = Mock()
        mock_article2.url = "https://wired.com/article2"
        mock_rss.get_latest_articles.return_value = [
            mock_article1, mock_article2]
        mock_rss_class.return_value = mock_rss

        # Mock content extractor
        mock_extractor = Mock()
        mock_extracted1 = Mock()
        mock_extracted1.title = "Article 1"
        mock_extracted2 = Mock()
        mock_extracted2.title = "Article 2"
        mock_extractor.extract_from_url.side_effect = [
            mock_extracted1, mock_extracted2]
        mock_extractor_class.return_value = mock_extractor

        scraper = WiredArticleScraper()
        results = scraper.get_multiple_articles("security", 2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], mock_extracted1)
        self.assertEqual(results[1], mock_extracted2)

    @patch('the_data_packet.scrapers.wired_scraper.RSSClient')
    @patch('the_data_packet.scrapers.wired_scraper.WiredContentExtractor')
    def test_get_multiple_articles_partial_failure(self, mock_extractor_class, mock_rss_class):
        """Test handling partial failures when extracting multiple articles."""
        # Mock RSS client
        mock_rss = Mock()
        mock_article1 = Mock()
        mock_article1.url = "https://wired.com/article1"
        mock_article2 = Mock()
        mock_article2.url = "https://wired.com/article2"
        mock_rss.get_latest_articles.return_value = [
            mock_article1, mock_article2]
        mock_rss_class.return_value = mock_rss

        # Mock content extractor - first succeeds, second fails
        mock_extractor = Mock()
        mock_extracted1 = Mock()
        mock_extracted1.title = "Article 1"
        mock_extractor.extract_from_url.side_effect = [
            mock_extracted1, Exception("Extraction failed")]
        mock_extractor_class.return_value = mock_extractor

        scraper = WiredArticleScraper()
        results = scraper.get_multiple_articles("security", 2)

        # Should return only successful extractions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], mock_extracted1)

    def test_get_multiple_articles_invalid_count(self):
        """Test handling invalid count parameter."""
        scraper = WiredArticleScraper()

        with self.assertRaises(ValueError) as cm:
            scraper.get_multiple_articles("security", 0)

        self.assertIn("Count must be positive", str(cm.exception))

    @patch('the_data_packet.scrapers.wired_scraper.RSSClient')
    @patch('the_data_packet.scrapers.wired_scraper.WiredContentExtractor')
    def test_scrape_article_from_url_success(self, mock_extractor_class, mock_rss_class):
        """Test successful article scraping from URL."""
        mock_extractor = Mock()
        mock_extracted = Mock()
        mock_extracted.title = "Direct URL Article"
        mock_extractor.extract_from_url.return_value = mock_extracted
        mock_extractor_class.return_value = mock_extractor

        scraper = WiredArticleScraper()
        result = scraper.scrape_article_from_url("https://wired.com/direct")

        self.assertEqual(result, mock_extracted)
        mock_extractor.extract_from_url.assert_called_once_with(
            "https://wired.com/direct")

    @patch('the_data_packet.scrapers.wired_scraper.WiredContentExtractor')
    def test_scrape_article_from_url_failure(self, mock_extractor_class):
        """Test handling extraction failure from URL."""
        mock_extractor = Mock()
        mock_extractor.extract_from_url.side_effect = Exception(
            "Network error")
        mock_extractor_class.return_value = mock_extractor

        scraper = WiredArticleScraper()

        with self.assertRaises(Exception) as cm:
            scraper.scrape_article_from_url("https://invalid-url.com")

        self.assertIn("Network error", str(cm.exception))

    def test_close_method(self):
        """Test scraper cleanup."""
        scraper = WiredArticleScraper()
        # Should not raise any exceptions
        scraper.close()

    def test_context_manager(self):
        """Test scraper as context manager."""
        with patch.object(WiredArticleScraper, 'close') as mock_close:
            with WiredArticleScraper() as scraper:
                self.assertIsInstance(scraper, WiredArticleScraper)

            mock_close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
