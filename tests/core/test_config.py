"""Unit tests for core.config module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from the_data_packet.core.config import Config, get_config, reset_config
from the_data_packet.core.exceptions import ConfigurationError


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def setUp(self):
        """Set up test fixtures."""
        reset_config()  # Reset global config before each test

    def tearDown(self):
        """Clean up after tests."""
        reset_config()  # Reset global config after each test

    def test_default_config_creation(self):
        """Test that config can be created with defaults."""
        config = Config()

        # Test default values
        self.assertEqual(config.show_name, "The Data Packet")
        self.assertEqual(config.max_articles_per_source, 1)
        self.assertEqual(config.article_sources, ["wired", "techcrunch"])
        self.assertEqual(config.article_categories, ["security", "ai"])
        self.assertEqual(config.claude_model, "claude-sonnet-4-5-20250929")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.aws_region, "us-east-1")
        self.assertTrue(config.generate_script)
        self.assertTrue(config.generate_audio)
        self.assertTrue(config.generate_rss)
        self.assertFalse(config.save_intermediate_files)
        self.assertTrue(config.cleanup_temp_files)

    def test_config_with_overrides(self):
        """Test config creation with parameter overrides."""
        config = Config(
            show_name="Test Podcast",
            max_articles_per_source=3,
            temperature=0.5,
            generate_audio=False,
        )

        self.assertEqual(config.show_name, "Test Podcast")
        self.assertEqual(config.max_articles_per_source, 3)
        self.assertEqual(config.temperature, 0.5)
        self.assertFalse(config.generate_audio)

    @patch.dict(
        os.environ,
        {
            "ANTHROPIC_API_KEY": "test-anthropic-key",
            "ELEVENLABS_API_KEY": "test-elevenlabs-key",
            "AWS_ACCESS_KEY_ID": "test-access-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret-key",
            "S3_BUCKET_NAME": "test-bucket",
            "SHOW_NAME": "Environment Podcast",
            "LOG_LEVEL": "DEBUG",
            "MAX_ARTICLES_PER_SOURCE": "5",
        },
    )
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        config = Config()

        self.assertEqual(config.anthropic_api_key, "test-anthropic-key")
        self.assertEqual(config.elevenlabs_api_key, "test-elevenlabs-key")
        self.assertEqual(config.aws_access_key_id, "test-access-key")
        self.assertEqual(config.aws_secret_access_key, "test-secret-key")
        self.assertEqual(config.s3_bucket_name, "test-bucket")
        self.assertEqual(config.show_name, "Environment Podcast")
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.max_articles_per_source, 5)

    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "new_output_dir"
            Config(output_directory=output_path)

            self.assertTrue(output_path.exists())
            self.assertTrue(output_path.is_dir())

    def test_validate_for_script_generation_success(self):
        """Test script generation validation with valid API key."""
        config = Config(anthropic_api_key="test-key")

        # Should not raise an exception
        config.validate_for_script_generation()

    def test_validate_for_script_generation_failure(self):
        """Test script generation validation without API key."""
        config = Config()

        with self.assertRaises(ConfigurationError) as cm:
            config.validate_for_script_generation()

        self.assertIn("Anthropic API key is required", str(cm.exception))

    def test_validate_for_audio_generation_success(self):
        """Test audio generation validation with valid API key."""
        config = Config(elevenlabs_api_key="test-key")

        # Should not raise an exception
        config.validate_for_audio_generation()

    def test_validate_for_audio_generation_failure(self):
        """Test audio generation validation without API key."""
        config = Config()

        with self.assertRaises(ConfigurationError) as cm:
            config.validate_for_audio_generation()

        self.assertIn("ElevenLabs API key is required", str(cm.exception))

    def test_invalid_log_level_validation(self):
        """Test that invalid log level raises ConfigurationError."""
        with self.assertRaises(ConfigurationError) as cm:
            Config(log_level="INVALID")

        self.assertIn("Invalid log level", str(cm.exception))

    def test_invalid_source_validation(self):
        """Test that invalid source raises ConfigurationError."""
        with self.assertRaises(ConfigurationError) as cm:
            Config(article_sources=["invalid_source"])

        self.assertIn("Unknown source", str(cm.exception))

    def test_incompatible_source_category_validation(self):
        """Test that incompatible source-category combinations are caught."""
        with self.assertRaises(ConfigurationError) as cm:
            Config(
                article_sources=["wired"], article_categories=["nonexistent_category"]
            )

        self.assertIn("not supported by source", str(cm.exception))

    def test_get_sources_for_category(self):
        """Test getting sources that support a category."""
        config = Config()

        security_sources = config.get_sources_for_category("security")
        self.assertIn("wired", security_sources)
        self.assertIn("techcrunch", security_sources)

        ai_sources = config.get_sources_for_category("ai")
        self.assertIn("wired", ai_sources)
        self.assertIn("techcrunch", ai_sources)

    def test_get_categories_for_source(self):
        """Test getting categories supported by a source."""
        config = Config()

        wired_categories = config.get_categories_for_source("wired")
        self.assertIn("security", wired_categories)
        self.assertIn("ai", wired_categories)

        techcrunch_categories = config.get_categories_for_source("techcrunch")
        self.assertIn("security", techcrunch_categories)
        self.assertIn("ai", techcrunch_categories)

    def test_get_categories_for_unknown_source(self):
        """Test getting categories for unknown source."""
        config = Config()

        unknown_categories = config.get_categories_for_source("unknown")
        self.assertEqual(unknown_categories, [])

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = Config(show_name="Test Show")

        config_dict = config.to_dict()

        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["show_name"], "Test Show")
        # Path should be converted to string
        self.assertIsInstance(config_dict["output_directory"], str)

    def test_global_config_singleton(self):
        """Test that get_config returns singleton."""
        config1 = get_config()
        config2 = get_config()

        self.assertIs(config1, config2)

    def test_global_config_with_overrides(self):
        """Test that overrides create new config instance."""
        config1 = get_config()
        config2 = get_config(show_name="Different Show")

        self.assertIsNot(config1, config2)
        self.assertEqual(config2.show_name, "Different Show")

    def test_reset_config(self):
        """Test config reset functionality."""
        config1 = get_config(show_name="Test")
        reset_config()
        config2 = get_config()

        self.assertIsNot(config1, config2)
        self.assertEqual(config2.show_name, "The Data Packet")  # Default


if __name__ == "__main__":
    unittest.main()
