"""Integration tests for the_data_packet package."""

import unittest
from unittest.mock import Mock, patch

from the_data_packet import ArticleData, WiredArticleScraper


class TestPackageIntegration(unittest.TestCase):
    """Integration tests for the complete package."""

    def test_package_imports(self):
        """Test that all main components can be imported from the package."""
        from the_data_packet import (
            ArticleData,
            HTTPClient,
            RSSClient,
            WiredArticleScraper,
            WiredContentExtractor,
            __version__,
        )

        # Test new module imports
        from the_data_packet.ai import ClaudeClient, ScriptGenerator
        from the_data_packet.audio import GeminiTTSGenerator
        from the_data_packet.config import Settings
        from the_data_packet.core import get_logger, setup_logging
        from the_data_packet.workflows import PipelineConfig, PodcastPipeline

        # Verify classes can be instantiated
        scraper = WiredArticleScraper()
        article = ArticleData()
        settings = Settings()
        config = PipelineConfig()

        self.assertIsNotNone(scraper)
        self.assertIsNotNone(article)
        self.assertIsNotNone(settings)
        self.assertIsNotNone(config)
        self.assertIsNotNone(__version__)

    @patch("the_data_packet.clients.rss_client.feedparser")
    @patch("the_data_packet.clients.http_client.requests")
    def test_end_to_end_latest_article_flow(self, mock_requests, mock_feedparser):
        """Test complete flow from RSS to extracted article."""
        # Mock RSS feed response
        mock_feed = Mock()
        mock_feed.entries = [
            {"link": "https://www.wired.com/story/test-article/"}]
        mock_feedparser.parse.return_value = mock_feed

        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = """
        <html>
        <head>
            <title>Test Article | WIRED</title>
            <meta name="author" content="Test Author">
        </head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>This is a test article with substantial content for testing.</p>
                <p>It has multiple paragraphs to ensure proper extraction.</p>
            </article>
        </body>
        </html>
        """
        mock_response.status_code = 200
        mock_requests.Session().get.return_value = mock_response

        # Create scraper and get article
        scraper = WiredArticleScraper()
        article = scraper.get_latest_security_article()

        # Verify results
        self.assertIsInstance(article, ArticleData)
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.author, "Test Author")
        self.assertEqual(article.category, "security")
        self.assertIn("test article", article.content.lower())
        self.assertTrue(article.is_valid())

        scraper.close()

    @patch("the_data_packet.clients.rss_client.feedparser")
    @patch("the_data_packet.clients.http_client.requests")
    def test_end_to_end_both_articles_flow(self, mock_requests, mock_feedparser):
        """Test complete flow for getting both latest articles."""
        # Mock RSS feed responses for both categories
        security_feed = Mock()
        security_feed.entries = [
            {"link": "https://www.wired.com/story/security-article/"}
        ]

        guide_feed = Mock()
        guide_feed.entries = [
            {"link": "https://www.wired.com/story/guide-article/"}]

        # Mock feedparser to return different feeds based on URL
        def mock_parse(url):
            if "security" in url:
                return security_feed
            else:
                return guide_feed

        mock_feedparser.parse.side_effect = mock_parse

        # Mock HTTP responses
        def mock_get(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200

            if "security-article" in url:
                mock_response.text = """
                <html>
                <head><title>Security Article | WIRED</title></head>
                <body>
                    <article>
                        <p>This is a security-focused article with important information.</p>
                    </article>
                </body>
                </html>
                """
            else:
                mock_response.text = """
                <html>
                <head><title>Guide Article | WIRED</title></head>
                <body>
                    <article>
                        <p>This is a comprehensive guide article with helpful tips.</p>
                    </article>
                </body>
                </html>
                """

            return mock_response

        mock_requests.Session().get.side_effect = mock_get

        # Create scraper and get both articles
        scraper = WiredArticleScraper()
        articles = scraper.get_both_latest_articles()

        # Verify results
        self.assertIn("security", articles)
        self.assertIn("guide", articles)

        security_article = articles["security"]
        guide_article = articles["guide"]

        self.assertEqual(security_article.title, "Security Article")
        self.assertEqual(guide_article.title, "Guide Article")
        self.assertEqual(security_article.category, "security")
        self.assertEqual(guide_article.category, "guide")
        self.assertIn("security-focused", security_article.content)
        self.assertIn("comprehensive guide", guide_article.content)

        scraper.close()

    def test_article_data_workflow(self):
        """Test ArticleData creation and manipulation workflow."""
        # Create article from dictionary
        data = {
            "title": "Test Article",
            "author": "Test Author",
            "content": "This is test content.",
            "url": "https://example.com",
            "category": "test",
        }

        article = ArticleData.from_dict(data)

        # Verify data integrity
        self.assertTrue(article.is_valid())
        self.assertEqual(article.to_dict(), data)

        # Test modification
        article.category = "modified"
        self.assertEqual(article.category, "modified")

        # Test invalid article
        invalid_article = ArticleData(title="", content="")
        self.assertFalse(invalid_article.is_valid())

    def test_error_propagation(self):
        """Test that errors are properly propagated through the system."""
        scraper = WiredArticleScraper()

        # Test invalid category
        with self.assertRaises(RuntimeError):
            scraper.get_latest_article("nonexistent")

        scraper.close()

    @patch("the_data_packet.clients.http_client.requests.Session")
    def test_resource_cleanup(self, mock_session_class):
        """Test that resources are properly cleaned up."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = WiredArticleScraper()
        scraper.close()

        # Verify session was closed
        mock_session.close.assert_called_once()
