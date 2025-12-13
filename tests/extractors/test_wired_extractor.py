"""Tests for extractors wired_extractor module."""

import unittest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from the_data_packet.extractors.wired_extractor import WiredContentExtractor


class TestWiredContentExtractor(unittest.TestCase):
    """Test cases for WiredContentExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = WiredContentExtractor()
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Article Title | WIRED</title>
            <meta name="author" content="Test Author">
            <meta property="og:title" content="Test Article Title">
        </head>
        <body>
            <article>
                <h1>Test Article Title</h1>
                <p>This is the first paragraph.</p>
                <p>This is the second paragraph.</p>
            </article>
        </body>
        </html>
        """

    def test_initialization(self):
        """Test WiredContentExtractor initialization."""
        extractor = WiredContentExtractor()
        self.assertIsNotNone(extractor)

    def test_extract_title_from_h1(self):
        """Test extracting title from h1 tag."""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        title = self.extractor._extract_title(soup)
        self.assertEqual(title, "Test Article Title")

    def test_extract_title_from_meta_og(self):
        """Test extracting title from og:title meta tag."""
        html = """
        <html>
        <head>
            <meta property="og:title" content="OG Title">
        </head>
        <body></body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        title = self.extractor._extract_title(soup)
        self.assertEqual(title, "OG Title")

    def test_extract_title_from_title_tag(self):
        """Test extracting title from title tag."""
        html = """
        <html>
        <head>
            <title>Page Title | WIRED</title>
        </head>
        <body></body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        title = self.extractor._extract_title(soup)
        self.assertEqual(title, "Page Title | WIRED")

    def test_extract_author_from_meta(self):
        """Test extracting author from meta tag."""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        author = self.extractor._extract_author(soup)
        self.assertEqual(author, "Test Author")

    def test_extract_author_missing(self):
        """Test extracting author when meta tag is missing."""
        html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        author = self.extractor._extract_author(soup)
        self.assertEqual(author, "")

    def test_extract_content_from_article(self):
        """Test extracting content from article tag."""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        content = self.extractor._extract_content(soup)
        self.assertIn("first paragraph", content)
        self.assertIn("second paragraph", content)

    def test_extract_content_missing_article(self):
        """Test extracting content when article tag is missing."""
        html = """
        <html>
        <body>
            <div>
                <p>Some content here.</p>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content = self.extractor._extract_content(soup)
        self.assertIn("Some content here", content)

    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "  Some text with   extra   spaces  \\n\\n  "
        clean_text = self.extractor._clean_text(dirty_text)
        self.assertEqual(clean_text, "Some text with extra spaces")

    def test_clean_text_with_html(self):
        """Test cleaning text that contains HTML entities."""
        html_text = "Text with &nbsp; and &amp; entities"
        clean_text = self.extractor._clean_text(html_text)
        # Should handle basic HTML entities
        self.assertNotIn("&nbsp;", clean_text)

    def test_extract_from_url_success(self):
        """Test successful extraction from URL."""
        mock_response = Mock()
        mock_response.text = self.sample_html
        mock_response.raise_for_status.return_value = None

        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response

            result = self.extractor.extract_from_url(
                "https://wired.com/article")

            self.assertEqual(result.title, "Test Article Title")
            self.assertEqual(result.author, "Test Author")
            self.assertIn("first paragraph", result.content)
            self.assertEqual(result.url, "https://wired.com/article")

    def test_extract_from_url_http_error(self):
        """Test extraction handles HTTP errors."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("HTTP Error")

            with self.assertRaises(Exception):
                self.extractor.extract_from_url("https://invalid-url.com")

    def test_extract_from_html_success(self):
        """Test successful extraction from HTML string."""
        result = self.extractor.extract_from_html(
            self.sample_html,
            url="https://example.com"
        )

        self.assertEqual(result.title, "Test Article Title")
        self.assertEqual(result.author, "Test Author")
        self.assertIn("first paragraph", result.content)
        self.assertEqual(result.url, "https://example.com")

    def test_extract_from_html_empty(self):
        """Test extraction from empty HTML."""
        result = self.extractor.extract_from_html(
            "", url="https://example.com")

        self.assertEqual(result.title, "")
        self.assertEqual(result.author, "")
        self.assertEqual(result.content, "")
        self.assertEqual(result.url, "https://example.com")

    def test_extract_from_soup(self):
        """Test extraction from BeautifulSoup object."""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        result = self.extractor.extract_from_soup(
            soup, url="https://example.com")

        self.assertEqual(result.title, "Test Article Title")
        self.assertEqual(result.author, "Test Author")
        self.assertIn("first paragraph", result.content)
        self.assertEqual(result.url, "https://example.com")


if __name__ == '__main__':
    unittest.main()
