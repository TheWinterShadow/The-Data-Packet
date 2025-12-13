"""Tests for claude_client module."""

import unittest
from unittest.mock import Mock, patch, MagicMock

from the_data_packet.ai.claude_client import ClaudeClient


class TestClaudeClient(unittest.TestCase):
    """Test cases for ClaudeClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "sk-ant-test-key"

    def test_initialization_with_api_key(self):
        """Test ClaudeClient initialization with valid API key."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            client = ClaudeClient(self.api_key)

            self.assertEqual(client.api_key, self.api_key)
            mock_anthropic.assert_called_once_with(api_key=self.api_key)

    def test_initialization_without_api_key(self):
        """Test ClaudeClient initialization fails without API key."""
        with self.assertRaises(ValueError) as cm:
            ClaudeClient(None)

        self.assertIn("Anthropic API key is required", str(cm.exception))

    def test_initialization_empty_api_key(self):
        """Test ClaudeClient initialization fails with empty API key."""
        with self.assertRaises(ValueError) as cm:
            ClaudeClient("")

        self.assertIn("Anthropic API key is required", str(cm.exception))

    @patch('anthropic.Anthropic')
    def test_generate_content_success(self, mock_anthropic):
        """Test successful content generation."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated response text"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Test
        client = ClaudeClient(self.api_key)
        result = client.generate_content("Test prompt")

        # Verify
        self.assertEqual(result, "Generated response text")
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": "Test prompt"}]
        )

    @patch('anthropic.Anthropic')
    def test_generate_content_with_custom_model(self, mock_anthropic):
        """Test content generation with custom model."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(self.api_key)
        result = client.generate_content(
            "Test prompt", model="claude-3-haiku-20240307")

        self.assertEqual(result, "Generated response")
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            messages=[{"role": "user", "content": "Test prompt"}]
        )

    @patch('anthropic.Anthropic')
    def test_generate_content_with_custom_max_tokens(self, mock_anthropic):
        """Test content generation with custom max tokens."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(self.api_key)
        result = client.generate_content("Test prompt", max_tokens=2000)

        self.assertEqual(result, "Generated response")
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": "Test prompt"}]
        )

    @patch('anthropic.Anthropic')
    def test_generate_content_api_error(self, mock_anthropic):
        """Test content generation handles API errors."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(self.api_key)

        with self.assertRaises(Exception) as cm:
            client.generate_content("Test prompt")

        self.assertIn("API Error", str(cm.exception))

    @patch('anthropic.Anthropic')
    def test_generate_content_empty_response(self, mock_anthropic):
        """Test content generation with empty response content."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(self.api_key)
        result = client.generate_content("Test prompt")

        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()
