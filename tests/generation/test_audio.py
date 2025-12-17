"""Unit tests for generation.audio module."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from the_data_packet.core.exceptions import AudioGenerationError, ConfigurationError
from the_data_packet.generation.audio import AudioGenerator, AudioResult


class TestAudioResult(unittest.TestCase):
    """Test cases for AudioResult dataclass."""

    def test_audio_result_creation(self):
        """Test AudioResult creation with minimum required fields."""
        result = AudioResult(output_file=Path("test.mp3"))

        self.assertEqual(result.output_file, Path("test.mp3"))
        self.assertIsNone(result.duration_seconds)
        self.assertIsNone(result.file_size_bytes)
        self.assertIsNone(result.generation_time_seconds)

    def test_audio_result_with_all_fields(self):
        """Test AudioResult creation with all fields."""
        result = AudioResult(
            output_file=Path("test.mp3"),
            duration_seconds=120.5,
            file_size_bytes=1024000,
            generation_time_seconds=45.2,
        )

        self.assertEqual(result.output_file, Path("test.mp3"))
        self.assertEqual(result.duration_seconds, 120.5)
        self.assertEqual(result.file_size_bytes, 1024000)
        self.assertEqual(result.generation_time_seconds, 45.2)


class TestAudioGenerator(unittest.TestCase):
    """Test cases for AudioGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.elevenlabs_api_key = "test-api-key"
        self.mock_config.tts_model = "eleven_turbo_v2_5"
        self.mock_config.voice_a = "voice-a-id"
        self.mock_config.voice_b = "voice-b-id"
        self.mock_config.output_directory = Path("/tmp/test")

    def test_available_models_defined(self):
        """Test that available models are properly defined."""
        self.assertIsInstance(AudioGenerator.AVAILABLE_MODELS, dict)
        self.assertIn("eleven_turbo_v2_5", AudioGenerator.AVAILABLE_MODELS)
        self.assertIn("eleven_multilingual_v2", AudioGenerator.AVAILABLE_MODELS)
        self.assertIn("eleven_flash_v2_5", AudioGenerator.AVAILABLE_MODELS)

    def test_default_voices_defined(self):
        """Test that default voices are properly defined."""
        self.assertIsInstance(AudioGenerator.DEFAULT_VOICES, dict)
        self.assertIn("male", AudioGenerator.DEFAULT_VOICES)
        self.assertIn("female", AudioGenerator.DEFAULT_VOICES)
        self.assertIsInstance(AudioGenerator.DEFAULT_VOICES["male"], list)
        self.assertIsInstance(AudioGenerator.DEFAULT_VOICES["female"], list)

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_init_with_api_key(self, mock_elevenlabs, mock_get_config):
        """Test AudioGenerator initialization with API key."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator(api_key="test-key")

        self.assertEqual(generator.api_key, "test-key")
        self.assertEqual(generator.model_id, "eleven_turbo_v2_5")
        mock_elevenlabs.assert_called_once_with(api_key="test-key")

    @patch("the_data_packet.generation.audio.get_config")
    def test_init_without_api_key_raises_error(self, mock_get_config):
        """Test that initialization without API key raises ConfigurationError."""
        mock_config_no_key = Mock()
        mock_config_no_key.elevenlabs_api_key = None
        mock_get_config.return_value = mock_config_no_key

        with self.assertRaises(ConfigurationError) as cm:
            AudioGenerator()

        self.assertIn("ElevenLabs API key is required", str(cm.exception))

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_init_with_custom_voices(self, mock_elevenlabs, mock_get_config):
        """Test AudioGenerator initialization with custom voices."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator(
            api_key="test-key", voice_a="custom-voice-a", voice_b="custom-voice-b"
        )

        self.assertEqual(generator.voice_a, "custom-voice-a")
        self.assertEqual(generator.voice_b, "custom-voice-b")

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_validate_voices_with_available_voices(
        self, mock_elevenlabs, mock_get_config
    ):
        """Test voice validation with available voices."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_voice_response = Mock()
        mock_voice_response.voices = [
            Mock(voice_id="voice-a-id"),
            Mock(voice_id="voice-b-id"),
            Mock(voice_id="other-voice"),
        ]
        mock_client.voices.get_all.return_value = mock_voice_response
        mock_elevenlabs.return_value = mock_client

        # Should not raise an exception
        generator = AudioGenerator(api_key="test-key")
        self.assertIsNotNone(generator)

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_audio_with_empty_script_raises_error(
        self, mock_elevenlabs, mock_get_config
    ):
        """Test that empty script raises AudioGenerationError."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator(api_key="test-key")

        with self.assertRaises(AudioGenerationError) as cm:
            generator.generate_audio("")

        self.assertIn("Script too short or empty", str(cm.exception))

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_audio_with_short_script_raises_error(
        self, mock_elevenlabs, mock_get_config
    ):
        """Test that very short script raises AudioGenerationError."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator(api_key="test-key")

        with self.assertRaises(AudioGenerationError) as cm:
            generator.generate_audio("Short")

        self.assertIn("Script too short or empty", str(cm.exception))

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_parse_script_for_speakers(self, mock_elevenlabs, mock_get_config):
        """Test script parsing for speaker identification."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator(api_key="test-key")

        script = """
        Alex: Welcome to the show!
        Sam: Thanks for having me.
        This is a narrator line.
        Alex: Let's talk about tech.
        """

        segments = generator._parse_script_for_speakers(script)

        self.assertEqual(len(segments), 4)
        self.assertEqual(segments[0]["text"], "Welcome to the show!")
        self.assertEqual(segments[0]["speaker"], "Alex")
        self.assertEqual(segments[1]["text"], "Thanks for having me.")
        self.assertEqual(segments[1]["speaker"], "Sam")
        self.assertEqual(segments[2]["text"], "This is a narrator line.")
        self.assertEqual(segments[2]["speaker"], "Alex")  # Default to Alex
        self.assertEqual(segments[3]["text"], "Let's talk about tech.")
        self.assertEqual(segments[3]["speaker"], "Alex")

    def test_get_available_voices_structure(self):
        """Test get_available_voices returns proper structure."""
        with patch("the_data_packet.generation.audio.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch(
                "the_data_packet.generation.audio.ElevenLabs"
            ) as mock_elevenlabs:
                mock_client = Mock()
                mock_voice_response = Mock()
                mock_voice_response.voices = [Mock(voice_id="test-voice-1")]
                mock_client.voices.get_all.return_value = mock_voice_response
                mock_elevenlabs.return_value = mock_client

                generator = AudioGenerator(api_key="test-key")
                voices = generator.get_available_voices()

                self.assertIsInstance(voices, dict)
                self.assertIn("male", voices)
                self.assertIn("female", voices)

    def test_get_available_voices_with_exception(self):
        """Test get_available_voices returns defaults when API fails."""
        with patch("the_data_packet.generation.audio.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch(
                "the_data_packet.generation.audio.ElevenLabs"
            ) as mock_elevenlabs:
                mock_client = Mock()
                mock_client.voices.get_all.side_effect = Exception("API Error")
                mock_elevenlabs.return_value = mock_client

                generator = AudioGenerator(api_key="test-key")
                voices = generator.get_available_voices()

                # Should return default voices
                self.assertEqual(voices, AudioGenerator.DEFAULT_VOICES)

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_test_authentication_success(self, mock_elevenlabs, mock_get_config):
        """Test successful authentication test."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_client.voices.get_all.return_value = [Mock()]  # Non-empty list
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator(api_key="test-key")
        result = generator.test_authentication()

        self.assertTrue(result)

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_test_authentication_failure(self, mock_elevenlabs, mock_get_config):
        """Test failed authentication test."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_client.voices.get_all.side_effect = Exception("Auth failed")
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator(api_key="test-key")
        result = generator.test_authentication()

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
