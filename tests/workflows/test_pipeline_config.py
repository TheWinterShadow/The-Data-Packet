"""Tests for workflows pipeline_config module."""

import unittest
from pathlib import Path

from the_data_packet.workflows.pipeline_config import PipelineConfig


class TestPipelineConfig(unittest.TestCase):
    """Test cases for PipelineConfig class."""

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

    def test_get_script_path(self):
        """Test getting full script file path."""
        config = PipelineConfig(
            output_directory=Path("/test/output"),
            script_filename="test_script.txt"
        )

        script_path = config.get_script_path()
        expected_path = Path("/test/output/test_script.txt")
        self.assertEqual(script_path, expected_path)

    def test_get_audio_path(self):
        """Test getting full audio file path."""
        config = PipelineConfig(
            output_directory=Path("/test/output"),
            audio_filename="test_audio.wav"
        )

        audio_path = config.get_audio_path()
        expected_path = Path("/test/output/test_audio.wav")
        self.assertEqual(audio_path, expected_path)

    def test_str_representation(self):
        """Test string representation of PipelineConfig."""
        config = PipelineConfig(show_name="Test Show")

        str_repr = str(config)
        self.assertIn("Test Show", str_repr)
        self.assertIn("PipelineConfig", str_repr)


if __name__ == '__main__':
    unittest.main()
