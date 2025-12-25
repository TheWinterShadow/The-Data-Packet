"""Unit tests for generation.audio module."""

import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

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

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_audio_success(self, mock_elevenlabs, mock_get_config):
        """Test successful audio generation."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        # Mock successful audio generation
        mock_response = [b"audio_chunk_1", b"audio_chunk_2"]
        mock_client.text_to_speech.convert.return_value = mock_response

        # Create a longer script to pass validation
        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI.
Alex: That's right. The latest developments are fascinating.
Sam: Absolutely. Let's dive into the details."""

        generator = AudioGenerator(api_key="test-key")

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_exists,
            patch("builtins.open", mock_open()),
        ):

            mock_stat.return_value = Mock(st_size=1024)
            mock_exists.return_value = True

            result = generator.generate_audio(script)

            self.assertIsInstance(result, AudioResult)
            self.assertEqual(result.output_file.name, "episode.mp3")
            self.assertIsNotNone(result.generation_time_seconds)
            self.assertEqual(result.file_size_bytes, 1024)

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_audio_no_segments_found(self, mock_elevenlabs, mock_get_config):
        """Test audio generation when all segments fail to generate."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        # Mock complete failure for all text-to-speech calls
        mock_client.text_to_speech.convert.side_effect = Exception(
            "Complete API failure"
        )

        # Any script will generate segments, but TTS will fail
        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI."""

        generator = AudioGenerator(api_key="test-key")

        with self.assertRaises(AudioGenerationError) as context:
            generator.generate_audio(script)

        self.assertIn(
            "No audio segments were successfully generated", str(context.exception)
        )

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_audio_api_failure(self, mock_elevenlabs, mock_get_config):
        """Test audio generation with API failure."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        # Mock API failure
        mock_client.text_to_speech.convert.side_effect = Exception("API Error")

        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI."""

        generator = AudioGenerator(api_key="test-key")

        with self.assertRaises(AudioGenerationError) as context:
            generator.generate_audio(script)

        # This will fail at the voice generation step, not the initial generation
        self.assertIn(
            "No audio segments were successfully generated", str(context.exception)
        )

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_audio_with_custom_output_file(
        self, mock_elevenlabs, mock_get_config
    ):
        """Test audio generation with custom output file."""
        from pathlib import Path

        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        # Mock successful audio generation
        mock_response = [b"audio_chunk"]
        mock_client.text_to_speech.convert.return_value = mock_response

        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI."""

        generator = AudioGenerator(api_key="test-key")
        custom_output = Path("/custom/path/episode.mp3")

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_exists,
            patch("builtins.open", mock_open()),
        ):

            mock_stat.return_value = Mock(st_size=512)
            mock_exists.return_value = True

            result = generator.generate_audio(script, custom_output)

            self.assertEqual(result.output_file, custom_output)
            self.assertEqual(result.file_size_bytes, 512)

    def test_parse_script_for_speakers_complex_dialogue(self):
        """Test parsing complex dialogue with multiple speakers."""
        from the_data_packet.generation.audio import AudioGenerator

        with patch("the_data_packet.generation.audio.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.voice_a = "voice_a_id"
            mock_config.voice_b = "voice_b_id"
            mock_get_config.return_value = mock_config

            with patch("the_data_packet.generation.audio.ElevenLabs"):
                generator = AudioGenerator(api_key="test-key")

                script = """
Alex: Hello everyone, welcome to our show.
Sam: Thanks Alex. Today we're covering AI developments.
Alex: That's right. The field is moving rapidly.

[Some narrative text]

Sam: Let's start with the latest research.
Alex: Absolutely. The new models are impressive.
"""

                segments = generator._parse_script_for_speakers(script)

                # Should find the dialogue lines and ignore narrative
                dialogue_segments = [s for s in segments if s["text"].strip()]
                self.assertGreaterEqual(len(dialogue_segments), 4)

                # Check that voices are assigned correctly
                alex_segments = [s for s in segments if s["speaker"] == "Alex"]
                sam_segments = [s for s in segments if s["speaker"] == "Sam"]

                self.assertGreater(len(alex_segments), 0)
                self.assertGreater(len(sam_segments), 0)

                # All Alex segments should have voice_a
                for segment in alex_segments:
                    self.assertEqual(segment["voice"], "voice_a_id")

                # All Sam segments should have voice_b
                for segment in sam_segments:
                    self.assertEqual(segment["voice"], "voice_b_id")

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_with_individual_voices_success(
        self, mock_elevenlabs, mock_get_config
    ):
        """Test successful individual voice generation and combination."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        # Mock audio generation responses
        mock_client.text_to_speech.convert.side_effect = [
            [b"audio_chunk_1"],
            [b"audio_chunk_2"],
        ]

        generator = AudioGenerator(api_key="test-key")

        segments = [
            {"speaker": "Alex", "text": "Hello", "voice": "voice_a"},
            {"speaker": "Sam", "text": "Hi there", "voice": "voice_b"},
        ]

        audio_data = generator._generate_with_individual_voices(segments)

        # Should combine all chunks
        self.assertEqual(audio_data, b"audio_chunk_1audio_chunk_2")

        # Should call convert for each segment
        self.assertEqual(mock_client.text_to_speech.convert.call_count, 2)

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_with_individual_voices_partial_failure(
        self, mock_elevenlabs, mock_get_config
    ):
        """Test individual voice generation with partial failures."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        # Mock mixed success/failure responses
        def mock_convert_side_effect(*args, **kwargs):
            if kwargs["text"].startswith("Hello"):
                return [b"audio_chunk_1"]
            else:
                raise Exception("API Error for this segment")

        mock_client.text_to_speech.convert.side_effect = mock_convert_side_effect

        generator = AudioGenerator(api_key="test-key")

        segments = [
            {"speaker": "Alex", "text": "Hello", "voice": "voice_a"},
            {"speaker": "Sam", "text": "Hi there", "voice": "voice_b"},
        ]

        audio_data = generator._generate_with_individual_voices(segments)

        # Should still return partial success
        self.assertEqual(audio_data, b"audio_chunk_1")

    @patch("the_data_packet.generation.audio.get_config")
    @patch("the_data_packet.generation.audio.ElevenLabs")
    def test_generate_with_individual_voices_total_failure(
        self, mock_elevenlabs, mock_get_config
    ):
        """Test individual voice generation with total failure."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client

        # Mock all failures
        mock_client.text_to_speech.convert.side_effect = Exception("Total API failure")

        generator = AudioGenerator(api_key="test-key")

        segments = [
            {"speaker": "Alex", "text": "Hello", "voice": "voice_a"},
            {"speaker": "Sam", "text": "Hi there", "voice": "voice_b"},
        ]

        with self.assertRaises(AudioGenerationError) as context:
            generator._generate_with_individual_voices(segments)

        self.assertIn(
            "No audio segments were successfully generated", str(context.exception)
        )

    def test_save_audio_success(self):
        """Test successful audio file saving."""
        from pathlib import Path

        from the_data_packet.generation.audio import AudioGenerator

        with patch("the_data_packet.generation.audio.get_config") as mock_get_config:
            mock_config = Mock()
            mock_get_config.return_value = mock_config

            with patch("the_data_packet.generation.audio.ElevenLabs"):
                generator = AudioGenerator(api_key="test-key")

                audio_data = b"test_audio_data"
                output_file = Path("/test/output.mp3")

                with patch("builtins.open", mock_open()) as mock_file:
                    generator._save_audio(audio_data, output_file)

                    # Verify file was opened for binary write
                    mock_file.assert_called_once_with(output_file, "wb")
                    # Verify audio data was written
                    mock_file().write.assert_called_once_with(audio_data)

    def test_save_audio_failure(self):
        """Test audio file saving failure."""
        from pathlib import Path

        from the_data_packet.generation.audio import AudioGenerator

        with patch("the_data_packet.generation.audio.get_config") as mock_get_config:
            mock_config = Mock()
            mock_get_config.return_value = mock_config

            with patch("the_data_packet.generation.audio.ElevenLabs"):
                generator = AudioGenerator(api_key="test-key")

                audio_data = b"test_audio_data"
                output_file = Path("/test/output.mp3")

                with patch("builtins.open", side_effect=IOError("Permission denied")):
                    with self.assertRaises(AudioGenerationError) as context:
                        generator._save_audio(audio_data, output_file)

                    self.assertIn("Failed to save audio to", str(context.exception))


if __name__ == "__main__":
    unittest.main()
