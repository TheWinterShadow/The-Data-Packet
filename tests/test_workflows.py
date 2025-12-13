"""Tests for workflow modules."""

import unittest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
from datetime import datetime

from the_data_packet.workflows import PipelineConfig, PodcastPipeline


class TestPipelineConfig(unittest.TestCase):
    """Test cases for the PipelineConfig class."""

    def test_initialization_with_defaults(self):
        """Test PipelineConfig initialization with default values."""
        config = PipelineConfig()

        self.assertIsInstance(config.episode_date, str)
        self.assertEqual(config.show_name, "Tech Daily")
        self.assertEqual(config.categories, ["security", "guide"])
        self.assertTrue(config.generate_script)
        self.assertTrue(config.generate_audio)
        self.assertEqual(config.output_directory, Path("./output"))
        self.assertEqual(config.script_filename, "episode_script.txt")
        self.assertEqual(config.audio_filename, "episode.wav")

    def test_initialization_with_custom_values(self):
        """Test PipelineConfig initialization with custom values."""
        custom_date = "January 1, 2024"
        custom_output = Path("/custom/output")

        config = PipelineConfig(
            episode_date=custom_date,
            show_name="Custom Show",
            categories=["security"],
            generate_script=False,
            generate_audio=False,
            output_directory=custom_output,
            script_filename="custom_script.txt",
            audio_filename="custom_audio.wav",
            anthropic_api_key="test-anthropic-key",
            google_api_key="test-google-key",
            voice_a="Charon",
            voice_b="Aoede"
        )

        self.assertEqual(config.episode_date, custom_date)
        self.assertEqual(config.show_name, "Custom Show")
        self.assertEqual(config.categories, ["security"])
        self.assertFalse(config.generate_script)
        self.assertFalse(config.generate_audio)
        self.assertEqual(config.output_directory, custom_output)
        self.assertEqual(config.script_filename, "custom_script.txt")
        self.assertEqual(config.audio_filename, "custom_audio.wav")

    def test_validate_success(self):
        """Test successful validation."""
        config = PipelineConfig(
            anthropic_api_key="sk-ant-test-key",
            google_api_key="AIza-test-key"
        )

        errors = config.validate()
        self.assertEqual(errors, [])

    def test_validate_missing_anthropic_key_for_script(self):
        """Test validation fails when Anthropic key missing for script generation."""
        config = PipelineConfig(
            generate_script=True,
            anthropic_api_key=None
        )

        errors = config.validate()
        self.assertIn(
            "Anthropic API key is required for script generation", errors)

    def test_validate_missing_google_key_for_audio(self):
        """Test validation fails when Google key missing for audio generation."""
        config = PipelineConfig(
            generate_audio=True,
            google_api_key=None
        )

        errors = config.validate()
        self.assertIn(
            "Google API key is required for audio generation", errors)

    def test_validate_invalid_categories(self):
        """Test validation fails with invalid categories."""
        config = PipelineConfig(categories=["invalid_category"])

        errors = config.validate()
        self.assertTrue(any("Invalid category" in error for error in errors))

    def test_validate_empty_categories(self):
        """Test validation fails with empty categories."""
        config = PipelineConfig(categories=[])

        errors = config.validate()
        self.assertIn("At least one category must be specified", errors)

    def test_validate_invalid_voices(self):
        """Test validation fails with invalid voices."""
        config = PipelineConfig(
            voice_a="InvalidVoice",
            voice_b="AnotherInvalidVoice"
        )

        errors = config.validate()
        self.assertTrue(any("Invalid voice" in error for error in errors))


class TestPodcastPipeline(unittest.TestCase):
    """Test cases for the PodcastPipeline class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = PipelineConfig(
            anthropic_api_key="test-anthropic-key",
            google_api_key="test-google-key"
        )
        self.pipeline = PodcastPipeline(self.config)

    def test_initialization(self):
        """Test PodcastPipeline initialization."""
        self.assertEqual(self.pipeline.config, self.config)

    @patch('the_data_packet.workflows.WiredArticleScraper')
    @patch('the_data_packet.workflows.ScriptGenerator')
    @patch('the_data_packet.workflows.GeminiTTSGenerator')
    @patch('pathlib.Path.mkdir')
    def test_run_complete_pipeline(self, mock_mkdir, mock_tts_class, mock_script_gen_class, mock_scraper_class):
        """Test running complete pipeline (script + audio)."""
        # Mock scraper
        mock_scraper = Mock()
        mock_article = Mock()
        mock_article.title = "Test Article"
        mock_scraper.get_multiple_articles.return_value = [
            mock_article, mock_article]
        mock_scraper_class.return_value = mock_scraper

        # Mock script generator
        mock_script_gen = Mock()
        mock_script_gen.generate_script.return_value = "Generated script content"
        mock_script_gen_class.return_value = mock_script_gen

        # Mock TTS generator
        mock_tts = Mock()
        mock_audio_result = Mock()
        mock_audio_result.success = True
        mock_audio_result.output_file = Path("test_audio.wav")
        mock_tts.generate_audio.return_value = mock_audio_result
        mock_tts_class.return_value = mock_tts

        # Run pipeline
        with patch('builtins.open', create=True) as mock_open:
            result = self.pipeline.run()

        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.articles_scraped, 2)
        self.assertTrue(result.script_generated)
        self.assertTrue(result.audio_generated)

        # Verify components were called
        mock_scraper.get_multiple_articles.assert_called()
        mock_script_gen.generate_script.assert_called_once()
        mock_tts.generate_audio.assert_called_once()

    @patch('the_data_packet.workflows.WiredArticleScraper')
    @patch('the_data_packet.workflows.ScriptGenerator')
    @patch('pathlib.Path.mkdir')
    def test_run_script_only_pipeline(self, mock_mkdir, mock_script_gen_class, mock_scraper_class):
        """Test running script-only pipeline."""
        # Set config for script only
        self.config.generate_audio = False

        # Mock scraper
        mock_scraper = Mock()
        mock_article = Mock()
        mock_scraper.get_multiple_articles.return_value = [mock_article]
        mock_scraper_class.return_value = mock_scraper

        # Mock script generator
        mock_script_gen = Mock()
        mock_script_gen.generate_script.return_value = "Generated script content"
        mock_script_gen_class.return_value = mock_script_gen

        # Run pipeline
        with patch('builtins.open', create=True) as mock_open:
            result = self.pipeline.run()

        # Verify result
        self.assertTrue(result.success)
        self.assertTrue(result.script_generated)
        self.assertFalse(result.audio_generated)

    @patch('the_data_packet.workflows.WiredArticleScraper')
    def test_run_pipeline_scraping_failure(self, mock_scraper_class):
        """Test pipeline handles scraping failure."""
        # Mock scraper to raise exception
        mock_scraper = Mock()
        mock_scraper.get_multiple_articles.side_effect = Exception(
            "Scraping failed")
        mock_scraper_class.return_value = mock_scraper

        # Run pipeline
        result = self.pipeline.run()

        # Verify failure
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Scraping failed", result.error_message)

    def test_run_pipeline_no_articles(self):
        """Test pipeline handles no articles found."""
        with patch('the_data_packet.workflows.WiredArticleScraper') as mock_scraper_class:
            mock_scraper = Mock()
            mock_scraper.get_multiple_articles.return_value = []
            mock_scraper_class.return_value = mock_scraper

            result = self.pipeline.run()

            self.assertFalse(result.success)
            self.assertIn("No articles", result.error_message)


if __name__ == '__main__':
    unittest.main()
