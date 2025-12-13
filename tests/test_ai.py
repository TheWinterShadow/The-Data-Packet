"""Tests for AI modules."""

import unittest
from unittest.mock import MagicMock, patch, Mock

from the_data_packet.ai import ClaudeClient, PodcastScriptGenerator
from the_data_packet.models import ArticleData


class TestClaudeClient(unittest.TestCase):
    """Test cases for the ClaudeClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.client = ClaudeClient(self.api_key)

    def test_initialization(self):
        """Test ClaudeClient initialization."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertIsNotNone(self.client.client)

    @patch('anthropic.Anthropic')
    def test_client_creation(self, mock_anthropic):
        """Test that Anthropic client is created properly."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        client = ClaudeClient("test-key")
        mock_anthropic.assert_called_once_with(api_key="test-key")

    @patch('anthropic.Anthropic')
    def test_generate_content(self, mock_anthropic):
        """Test content generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated content")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient("test-key")
        result = client.generate_content("Test prompt")

        self.assertEqual(result, "Generated content")
        mock_client.messages.create.assert_called_once()

    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        with self.assertRaises(ValueError):
            ClaudeClient(None)


class TestScriptGenerator(unittest.TestCase):
    """Test cases for the ScriptGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_claude = MagicMock()
        self.generator = ScriptGenerator(self.mock_claude)

    def test_initialization(self):
        """Test ScriptGenerator initialization."""
        self.assertEqual(self.generator.claude_client, self.mock_claude)

    def test_generate_script_with_articles(self):
        """Test script generation with articles."""
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

        self.mock_claude.generate_content.return_value = "Generated script content"

        result = self.generator.generate_script(
            articles=articles,
            show_name="Test Show",
            episode_date="January 1, 2024"
        )

        self.assertEqual(result, "Generated script content")
        self.mock_claude.generate_content.assert_called_once()

        # Verify the prompt contains article information
        call_args = self.mock_claude.generate_content.call_args[0][0]
        self.assertIn("Test Article 1", call_args)
        self.assertIn("Test Article 2", call_args)
        self.assertIn("Test Show", call_args)
        self.assertIn("January 1, 2024", call_args)

    def test_generate_script_empty_articles(self):
        """Test script generation with empty articles list."""
        with self.assertRaises(ValueError):
            self.generator.generate_script([], "Test Show", "Jan 1, 2024")

    def test_generate_script_none_articles(self):
        """Test script generation with None articles."""
        with self.assertRaises(ValueError):
            self.generator.generate_script(None, "Test Show", "Jan 1, 2024")


if __name__ == '__main__':
    unittest.main()
