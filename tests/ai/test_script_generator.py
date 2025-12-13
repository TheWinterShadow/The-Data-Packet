"""Tests for script_generator module."""

import unittest
from unittest.mock import Mock, MagicMock

from the_data_packet.ai.script_generator import PodcastScriptGenerator
from the_data_packet.models import ArticleData


class TestScriptGenerator(unittest.TestCase):
    """Test cases for ScriptGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_claude_client = Mock()
        self.generator = ScriptGenerator(self.mock_claude_client)

    def test_initialization(self):
        """Test ScriptGenerator initialization."""
        self.assertEqual(self.generator.claude_client, self.mock_claude_client)

    def test_generate_script_success(self):
        """Test successful script generation."""
        # Setup test data
        articles = [
            ArticleData(
                title="Security Alert",
                author="John Doe",
                content="Important security information...",
                url="https://example.com/1",
                category="security"
            ),
            ArticleData(
                title="Tech Guide",
                author="Jane Smith",
                content="Helpful tech guidance...",
                url="https://example.com/2",
                category="guide"
            )
        ]

        expected_script = "Alex: Welcome to the show...\nSam: Thanks Alex..."
        self.mock_claude_client.generate_content.return_value = expected_script

        # Test generation
        result = self.generator.generate_script(
            articles=articles,
            show_name="Test Podcast",
            episode_date="January 1, 2024"
        )

        # Verify result
        self.assertEqual(result, expected_script)

        # Verify Claude client was called
        self.mock_claude_client.generate_content.assert_called_once()
        call_args = self.mock_claude_client.generate_content.call_args[0][0]

        # Verify prompt contains expected information
        self.assertIn("Test Podcast", call_args)
        self.assertIn("January 1, 2024", call_args)
        self.assertIn("Security Alert", call_args)
        self.assertIn("Tech Guide", call_args)

    def test_generate_script_empty_articles(self):
        """Test script generation with empty articles list."""
        with self.assertRaises(ValueError) as cm:
            self.generator.generate_script(
                articles=[],
                show_name="Test Podcast",
                episode_date="January 1, 2024"
            )

        self.assertIn("At least one article is required", str(cm.exception))

    def test_generate_script_none_articles(self):
        """Test script generation with None articles."""
        with self.assertRaises(ValueError) as cm:
            self.generator.generate_script(
                articles=None,
                show_name="Test Podcast",
                episode_date="January 1, 2024"
            )

        self.assertIn("At least one article is required", str(cm.exception))

    def test_generate_script_missing_show_name(self):
        """Test script generation fails without show name."""
        articles = [
            ArticleData(
                title="Test Article",
                author="Author",
                content="Content",
                url="https://example.com",
                category="security"
            )
        ]

        with self.assertRaises(ValueError) as cm:
            self.generator.generate_script(
                articles=articles,
                show_name="",
                episode_date="January 1, 2024"
            )

        self.assertIn("Show name is required", str(cm.exception))

    def test_generate_script_missing_episode_date(self):
        """Test script generation fails without episode date."""
        articles = [
            ArticleData(
                title="Test Article",
                author="Author",
                content="Content",
                url="https://example.com",
                category="security"
            )
        ]

        with self.assertRaises(ValueError) as cm:
            self.generator.generate_script(
                articles=articles,
                show_name="Test Podcast",
                episode_date=""
            )

        self.assertIn("Episode date is required", str(cm.exception))

    def test_format_articles_for_prompt(self):
        """Test article formatting for prompt."""
        articles = [
            ArticleData(
                title="Test Article 1",
                author="Author 1",
                content="Content 1",
                url="https://example.com/1",
                category="security"
            ),
            ArticleData(
                title="Test Article 2",
                author="Author 2",
                content="Content 2",
                url="https://example.com/2",
                category="guide"
            )
        ]

        formatted = self.generator._format_articles_for_prompt(articles)

        self.assertIn("Test Article 1", formatted)
        self.assertIn("Test Article 2", formatted)
        self.assertIn("Author 1", formatted)
        self.assertIn("Author 2", formatted)
        self.assertIn("Content 1", formatted)
        self.assertIn("Content 2", formatted)

    def test_claude_client_error_handling(self):
        """Test handling of Claude client errors."""
        articles = [
            ArticleData(
                title="Test Article",
                author="Author",
                content="Content",
                url="https://example.com",
                category="security"
            )
        ]

        self.mock_claude_client.generate_content.side_effect = Exception(
            "API Error")

        with self.assertRaises(Exception) as cm:
            self.generator.generate_script(
                articles=articles,
                show_name="Test Podcast",
                episode_date="January 1, 2024"
            )

        self.assertIn("API Error", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
