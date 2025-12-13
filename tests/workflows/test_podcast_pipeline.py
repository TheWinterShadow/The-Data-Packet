"""Tests for workflows podcast_pipeline module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from the_data_packet.workflows.podcast_pipeline import PodcastPipeline
from the_data_packet.workflows.pipeline_config import PipelineConfig


class TestPodcastPipeline(unittest.TestCase):
    """Test cases for PodcastPipeline class."""

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

    @patch('the_data_packet.workflows.podcast_pipeline.WiredArticleScraper')
    @patch('the_data_packet.workflows.podcast_pipeline.ScriptGenerator')
    @patch('the_data_packet.workflows.podcast_pipeline.GeminiTTSGenerator')
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

    @patch('the_data_packet.workflows.podcast_pipeline.WiredArticleScraper')
    @patch('the_data_packet.workflows.podcast_pipeline.ScriptGenerator')
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

    @patch('the_data_packet.workflows.podcast_pipeline.WiredArticleScraper')
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
        with patch('the_data_packet.workflows.podcast_pipeline.WiredArticleScraper') as mock_scraper_class:
            mock_scraper = Mock()
            mock_scraper.get_multiple_articles.return_value = []
            mock_scraper_class.return_value = mock_scraper

            result = self.pipeline.run()

            self.assertFalse(result.success)
            self.assertIn("No articles", result.error_message)

    @patch('the_data_packet.workflows.podcast_pipeline.WiredArticleScraper')
    @patch('the_data_packet.workflows.podcast_pipeline.ScriptGenerator')
    @patch('pathlib.Path.mkdir')
    def test_run_pipeline_script_generation_failure(self, mock_mkdir, mock_script_gen_class, mock_scraper_class):
        """Test pipeline handles script generation failure."""
        # Mock scraper
        mock_scraper = Mock()
        mock_article = Mock()
        mock_scraper.get_multiple_articles.return_value = [mock_article]
        mock_scraper_class.return_value = mock_scraper

        # Mock script generator to fail
        mock_script_gen = Mock()
        mock_script_gen.generate_script.side_effect = Exception(
            "Script generation failed")
        mock_script_gen_class.return_value = mock_script_gen

        # Run pipeline
        result = self.pipeline.run()

        # Verify failure
        self.assertFalse(result.success)
        self.assertIn("Script generation failed", result.error_message)

    def test_calculate_total_articles_needed(self):
        """Test calculation of total articles needed."""
        config = PipelineConfig(categories=["security", "guide"])
        pipeline = PodcastPipeline(config)

        total = pipeline._calculate_total_articles_needed()
        # Should be 2 (1 per category)
        self.assertEqual(total, 2)

    def test_create_pipeline_result_success(self):
        """Test creating successful pipeline result."""
        result = self.pipeline._create_pipeline_result(
            success=True,
            articles_scraped=3,
            script_generated=True,
            audio_generated=True,
            script_path=Path("script.txt"),
            audio_path=Path("audio.wav"),
            execution_time_seconds=15.5
        )

        self.assertTrue(result.success)
        self.assertEqual(result.articles_scraped, 3)
        self.assertTrue(result.script_generated)
        self.assertTrue(result.audio_generated)
        self.assertEqual(result.execution_time_seconds, 15.5)

    def test_create_pipeline_result_failure(self):
        """Test creating failure pipeline result."""
        result = self.pipeline._create_pipeline_result(
            success=False,
            error_message="Test error message"
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Test error message")


if __name__ == '__main__':
    unittest.main()
