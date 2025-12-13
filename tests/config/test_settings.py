"""Tests for config settings module."""

import unittest
from unittest.mock import patch
import os

from the_data_packet.config.settings import Settings
from the_data_packet.config.exceptions import ConfigurationError


class TestSettings(unittest.TestCase):
    """Test cases for Settings class."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_initialization(self):
        """Test Settings initialization with defaults."""
        settings = Settings()
        self.assertIsNone(settings.anthropic_api_key)
        self.assertIsNone(settings.google_api_key)
        self.assertEqual(settings.default_voice_a, "Puck")
        self.assertEqual(settings.default_voice_b, "Kore")

    def test_environment_variable_loading(self):
        """Test Settings loads from environment variables."""
        os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
        os.environ["GOOGLE_API_KEY"] = "test-google-key"

        settings = Settings()
        self.assertEqual(settings.anthropic_api_key, "test-anthropic-key")
        self.assertEqual(settings.google_api_key, "test-google-key")

    def test_gemini_api_key_fallback(self):
        """Test GEMINI_API_KEY fallback for Google API key."""
        os.environ["GEMINI_API_KEY"] = "test-gemini-key"

        settings = Settings()
        self.assertEqual(settings.google_api_key, "test-gemini-key")

    def test_google_api_key_takes_precedence(self):
        """Test GOOGLE_API_KEY takes precedence over GEMINI_API_KEY."""
        os.environ["GOOGLE_API_KEY"] = "test-google-key"
        os.environ["GEMINI_API_KEY"] = "test-gemini-key"

        settings = Settings()
        self.assertEqual(settings.google_api_key, "test-google-key")

    def test_validate_api_keys_success(self):
        """Test successful API key validation."""
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"
        os.environ["GOOGLE_API_KEY"] = "AIza-test-key"

        settings = Settings()
        # Should not raise any exception
        settings.validate_api_keys()

    def test_validate_api_keys_missing_anthropic(self):
        """Test validation fails when Anthropic API key is missing."""
        os.environ["GOOGLE_API_KEY"] = "AIza-test-key"

        settings = Settings()
        with self.assertRaises(ConfigurationError) as cm:
            settings.validate_api_keys()
        self.assertIn("Anthropic API key", str(cm.exception))

    def test_validate_api_keys_missing_google(self):
        """Test validation fails when Google API key is missing."""
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"

        settings = Settings()
        with self.assertRaises(ConfigurationError) as cm:
            settings.validate_api_keys()
        self.assertIn("Google API key", str(cm.exception))

    def test_available_voices(self):
        """Test available voices list."""
        settings = Settings()
        expected_voices = ["Puck", "Charon",
                           "Kore", "Fenrir", "Aoede", "Zephyr"]
        self.assertEqual(settings.available_voices, expected_voices)

    def test_validate_voice_valid(self):
        """Test voice validation with valid voice."""
        settings = Settings()
        # Should not raise exception
        settings.validate_voice("Puck")
        settings.validate_voice("Kore")

    def test_validate_voice_invalid(self):
        """Test voice validation with invalid voice."""
        settings = Settings()
        with self.assertRaises(ConfigurationError) as cm:
            settings.validate_voice("InvalidVoice")
        self.assertIn("Invalid voice", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
