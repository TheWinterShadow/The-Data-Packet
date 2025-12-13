"""Tests for CLI module."""

import json
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from the_data_packet.cli import format_article_output, main, setup_logging
from the_data_packet.models import ArticleData


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""

    def test_format_article_output_json(self):
        """Test JSON formatting of article output."""
        article = ArticleData(
            title="Test Title",
            author="Test Author",
            content="Test content",
            url="https://example.com",
            category="test",
        )

        output = format_article_output(article, "json")
        data = json.loads(output)

        self.assertEqual(data["title"], "Test Title")
        self.assertEqual(data["author"], "Test Author")
        self.assertEqual(data["content"], "Test content")
        self.assertEqual(data["url"], "https://example.com")
        self.assertEqual(data["category"], "test")

    def test_format_article_output_text(self):
        """Test text formatting of article output."""
        article = ArticleData(
            title="Test Title",
            author="Test Author",
            content="Test content with multiple words here.",
            url="https://example.com",
            category="test",
        )

        output = format_article_output(article, "text")

        self.assertIn("Title: Test Title", output)
        self.assertIn("Author: Test Author", output)
        self.assertIn("Category: test", output)
        self.assertIn("URL: https://example.com", output)
        self.assertIn("Content Length:", output)
        self.assertIn("Test content with multiple words here.", output)

    def test_format_article_output_text_none_values(self):
        """Test text formatting with None values."""
        article = ArticleData()

        output = format_article_output(article, "text")

        self.assertIn("Title: N/A", output)
        self.assertIn("Author: N/A", output)
        self.assertIn("Category: N/A", output)
        self.assertIn("URL: N/A", output)
        self.assertIn("Content Length: 0", output)

    def test_format_article_output_invalid_format(self):
        """Test handling of invalid format type."""
        article = ArticleData(title="Test")

        with self.assertRaises(ValueError) as cm:
            format_article_output(article, "invalid")
        self.assertIn("Unsupported format", str(cm.exception))

    @patch("the_data_packet.cli.logging.basicConfig")
    def test_setup_logging_default(self, mock_basic_config):
        """Test default logging setup."""
        setup_logging()

        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        self.assertEqual(kwargs["level"], 20)  # logging.INFO

    @patch("the_data_packet.cli.logging.basicConfig")
    def test_setup_logging_verbose(self, mock_basic_config):
        """Test verbose logging setup."""
        setup_logging(verbose=True)

        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        self.assertEqual(kwargs["level"], 10)  # logging.DEBUG

    @patch("the_data_packet.cli.WiredArticleScraper")
    @patch("sys.argv", ["cli.py", "security"])
    def test_main_security_article(self, mock_scraper_class):
        """Test CLI with security article request."""
        # Mock scraper and article
        mock_scraper = Mock()
        mock_article = ArticleData(
            title="Security Article",
            author="Security Author",
            content="Security content",
            category="security",
        )
        mock_scraper.get_latest_article.return_value = mock_article
        mock_scraper_class.return_value = mock_scraper

        # Capture output
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with patch("sys.exit"):  # Prevent actual exit
                try:
                    main()
                except SystemExit:
                    pass

        # Verify scraper calls
        mock_scraper.get_latest_article.assert_called_once_with("security")
        mock_scraper.close.assert_called_once()

        # Verify output contains expected data
        output = mock_stdout.getvalue()
        if output:  # Only check if output was captured
            data = json.loads(output)
            self.assertEqual(data["title"], "Security Article")
            self.assertEqual(data["category"], "security")

    @patch("the_data_packet.cli.WiredArticleScraper")
    @patch("sys.argv", ["cli.py", "both"])
    def test_main_both_articles(self, mock_scraper_class):
        """Test CLI with both articles request."""
        # Mock scraper and articles
        mock_scraper = Mock()
        security_article = ArticleData(
            title="Security", category="security", content="content"
        )
        guide_article = ArticleData(title="Guide", category="guide", content="content")
        mock_scraper.get_both_latest_articles.return_value = {
            "security": security_article,
            "guide": guide_article,
        }
        mock_scraper_class.return_value = mock_scraper

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with patch("sys.exit"):
                try:
                    main()
                except SystemExit:
                    pass

        mock_scraper.get_both_latest_articles.assert_called_once()
        mock_scraper.close.assert_called_once()

    @patch("the_data_packet.cli.WiredArticleScraper")
    @patch("sys.argv", ["cli.py", "--url", "https://example.com/article"])
    def test_main_specific_url(self, mock_scraper_class):
        """Test CLI with specific URL."""
        mock_scraper = Mock()
        mock_article = ArticleData(title="URL Article", content="content")
        mock_scraper.scrape_article_from_url.return_value = mock_article
        mock_scraper_class.return_value = mock_scraper

        with patch("sys.stdout", new_callable=StringIO):
            with patch("sys.exit"):
                try:
                    main()
                except SystemExit:
                    pass

        mock_scraper.scrape_article_from_url.assert_called_once_with(
            "https://example.com/article"
        )
        mock_scraper.close.assert_called_once()

    @patch("the_data_packet.cli.WiredArticleScraper")
    @patch("sys.argv", ["cli.py", "security", "--count", "3"])
    def test_main_multiple_articles(self, mock_scraper_class):
        """Test CLI with multiple articles request."""
        mock_scraper = Mock()
        mock_articles = [
            ArticleData(title="Article 1", content="content"),
            ArticleData(title="Article 2", content="content"),
            ArticleData(title="Article 3", content="content"),
        ]
        mock_scraper.get_multiple_articles.return_value = mock_articles
        mock_scraper_class.return_value = mock_scraper

        with patch("sys.stdout", new_callable=StringIO):
            with patch("sys.exit"):
                try:
                    main()
                except SystemExit:
                    pass

        mock_scraper.get_multiple_articles.assert_called_once_with("security", 3)
        mock_scraper.close.assert_called_once()

    @patch("sys.argv", ["cli.py"])
    def test_main_no_arguments(self):
        """Test CLI with no arguments (should show error)."""
        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit):
                main()

    @patch("sys.argv", ["cli.py", "security", "--url", "https://example.com"])
    def test_main_conflicting_arguments(self):
        """Test CLI with conflicting arguments."""
        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit):
                main()

    @patch("sys.argv", ["cli.py", "security", "--count", "15"])
    def test_main_invalid_count(self):
        """Test CLI with invalid count value."""
        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit):
                main()

    @patch("the_data_packet.cli.WiredArticleScraper")
    @patch("sys.argv", ["cli.py", "security"])
    def test_main_scraper_error(self, mock_scraper_class):
        """Test CLI handling of scraper errors."""
        mock_scraper = Mock()
        mock_scraper.get_latest_article.side_effect = RuntimeError("Scraper error")
        mock_scraper_class.return_value = mock_scraper

        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit) as exc_info:
                main()

        self.assertEqual(exc_info.exception.code, 1)
        mock_scraper.close.assert_called_once()

    @patch("the_data_packet.cli.WiredArticleScraper")
    @patch("sys.argv", ["cli.py", "security"])
    def test_main_keyboard_interrupt(self, mock_scraper_class):
        """Test CLI handling of keyboard interrupt."""
        mock_scraper = Mock()
        mock_scraper.get_latest_article.side_effect = KeyboardInterrupt()
        mock_scraper_class.return_value = mock_scraper

        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit) as exc_info:
                main()

        self.assertEqual(exc_info.exception.code, 1)
        mock_scraper.close.assert_called_once()
