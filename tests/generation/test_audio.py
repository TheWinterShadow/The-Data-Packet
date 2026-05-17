"""Unit tests for generation.audio module."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from the_data_packet.core.exceptions import AudioGenerationError, ConfigurationError
from the_data_packet.generation.audio import AudioGenerator, AudioResult


def _make_tts_response(pcm_data: bytes = b"\x00\x01" * 100) -> Mock:
    """Build a mock Vertex AI TTS response with PCM inline data."""
    mock_inline = Mock()
    mock_inline.data = pcm_data
    mock_part = Mock()
    mock_part.inline_data = mock_inline
    mock_content = Mock()
    mock_content.parts = [mock_part]
    mock_candidate = Mock()
    mock_candidate.content = mock_content
    mock_response = Mock()
    mock_response.candidates = [mock_candidate]
    return mock_response


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
        self.mock_config.male_voice = "Puck"
        self.mock_config.female_voice = "Kore"
        self.mock_config.google_cloud_project = "test-project"
        self.mock_config.output_directory = Path("/tmp/test")

    def _make_generator(self) -> AudioGenerator:
        """Create an AudioGenerator with mocked Vertex AI client."""
        with (
            patch("the_data_packet.generation.audio.get_config", return_value=self.mock_config),
            patch("the_data_packet.generation.audio.genai.Client"),
        ):
            return AudioGenerator()

    def test_available_voices_defined(self):
        """Test that available voices are properly defined."""
        self.assertIsInstance(AudioGenerator.AVAILABLE_VOICES, dict)
        self.assertIn("male", AudioGenerator.AVAILABLE_VOICES)
        self.assertIn("female", AudioGenerator.AVAILABLE_VOICES)
        self.assertIn("Puck", AudioGenerator.AVAILABLE_VOICES["male"])
        self.assertIn("Kore", AudioGenerator.AVAILABLE_VOICES["female"])

    def test_tts_model_defined(self):
        """Test that the TTS model constant is set."""
        self.assertEqual(AudioGenerator.TTS_MODEL, "gemini-3.1-flash-tts-preview")

    def test_sample_rate_defined(self):
        """Test that the sample rate is 24kHz (Vertex AI PCM output)."""
        self.assertEqual(AudioGenerator.SAMPLE_RATE, 24000)

    @patch("the_data_packet.generation.audio.genai.Client")
    @patch("the_data_packet.generation.audio.get_config")
    def test_init_success(self, mock_get_config, mock_genai_client):
        """Test AudioGenerator initializes correctly."""
        mock_get_config.return_value = self.mock_config
        mock_genai_client.return_value = Mock()

        generator = AudioGenerator()

        self.assertEqual(generator.male_voice, "Puck")
        self.assertEqual(generator.female_voice, "Kore")
        mock_genai_client.assert_called_once()

    @patch("the_data_packet.generation.audio.genai.Client")
    @patch("the_data_packet.generation.audio.get_config")
    def test_init_custom_voices(self, mock_get_config, mock_genai_client):
        """Test AudioGenerator accepts custom voice overrides."""
        mock_get_config.return_value = self.mock_config
        mock_genai_client.return_value = Mock()

        generator = AudioGenerator(male_voice="Charon", female_voice="Aoede")

        self.assertEqual(generator.male_voice, "Charon")
        self.assertEqual(generator.female_voice, "Aoede")

    @patch("the_data_packet.generation.audio.genai.Client")
    @patch("the_data_packet.generation.audio.get_config")
    def test_init_client_failure_raises_config_error(self, mock_get_config, mock_genai_client):
        """Test that a Vertex AI client init failure raises ConfigurationError."""
        mock_get_config.return_value = self.mock_config
        mock_genai_client.side_effect = Exception("Auth failed")

        with self.assertRaises(ConfigurationError) as cm:
            AudioGenerator()

        self.assertIn("Failed to initialize Vertex AI client", str(cm.exception))

    def test_parse_script_to_turns_basic(self):
        """Test script parsing into (speaker, text) turns."""
        generator = self._make_generator()
        script = """
Alex: Welcome to the show!
Sam: Thanks for having me.
Alex: Let's talk about tech.
"""
        turns = generator._parse_script_to_turns(script)

        self.assertEqual(len(turns), 3)
        self.assertEqual(turns[0], ("Alex", "Welcome to the show!"))
        self.assertEqual(turns[1], ("Sam", "Thanks for having me."))
        self.assertEqual(turns[2], ("Alex", "Let's talk about tech."))

    def test_parse_script_to_turns_skips_headers(self):
        """Test that headers and bold lines are skipped."""
        generator = self._make_generator()
        script = """
# Episode Title
**Introduction**
Alex: Hello everyone.
Sam: Hi there.
"""
        turns = generator._parse_script_to_turns(script)

        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0][0], "Alex")
        self.assertEqual(turns[1][0], "Sam")

    def test_parse_script_to_turns_narrator_defaults_to_alex(self):
        """Test that non-dialogue lines are assigned to Alex."""
        generator = self._make_generator()
        script = "Alex: Hello.\nThis is a narrator line.\nSam: Hi."
        turns = generator._parse_script_to_turns(script)

        narrator_turn = turns[1]
        self.assertEqual(narrator_turn[0], "Alex")
        self.assertEqual(narrator_turn[1], "This is a narrator line.")

    def test_parse_script_to_turns_empty_script(self):
        """Test that an empty script returns no turns."""
        generator = self._make_generator()
        self.assertEqual(generator._parse_script_to_turns(""), [])
        self.assertEqual(generator._parse_script_to_turns("   \n  \n  "), [])

    @patch("time.sleep")
    def test_synthesize_turns_calls_api_per_turn(self, _mock_sleep):
        """Test that _synthesize_turns makes one API call per turn."""
        generator = self._make_generator()
        generator.tts_client = Mock()
        generator.tts_client.models.generate_content.return_value = _make_tts_response()

        turns = [("Alex", "Hello."), ("Sam", "Hi there."), ("Alex", "Goodbye.")]
        generator._synthesize_turns(turns)

        self.assertEqual(generator.tts_client.models.generate_content.call_count, 3)

    @patch("time.sleep")
    def test_synthesize_turns_concatenates_pcm(self, _mock_sleep):
        """Test that PCM bytes from all turns are concatenated."""
        generator = self._make_generator()
        generator.tts_client = Mock()
        pcm_chunk = b"\xab\xcd" * 50
        generator.tts_client.models.generate_content.return_value = _make_tts_response(pcm_chunk)

        turns = [("Alex", "Hello."), ("Sam", "Hi.")]
        result = generator._synthesize_turns(turns)

        self.assertEqual(result, pcm_chunk + pcm_chunk)

    @patch("time.sleep")
    def test_synthesize_turns_uses_correct_voice_per_speaker(self, _mock_sleep):
        """Test that each speaker gets their assigned voice."""
        generator = self._make_generator()
        generator.tts_client = Mock()
        generator.tts_client.models.generate_content.return_value = _make_tts_response()

        turns = [("Alex", "Hello."), ("Sam", "Hi.")]
        generator._synthesize_turns(turns)

        calls = generator.tts_client.models.generate_content.call_args_list
        alex_config = calls[0].kwargs["config"]
        sam_config = calls[1].kwargs["config"]

        alex_voice = alex_config.speech_config.voice_config.prebuilt_voice_config.voice_name
        sam_voice = sam_config.speech_config.voice_config.prebuilt_voice_config.voice_name

        self.assertEqual(alex_voice, "Puck")
        self.assertEqual(sam_voice, "Kore")

    @patch("time.sleep")
    def test_synthesize_turns_api_failure_raises_error(self, _mock_sleep):
        """Test that a TTS API failure raises AudioGenerationError."""
        generator = self._make_generator()
        generator.tts_client = Mock()
        generator.tts_client.models.generate_content.side_effect = Exception("API error")

        with self.assertRaises(AudioGenerationError) as cm:
            generator._synthesize_turns([("Alex", "Hello.")])

        self.assertIn("Failed to synthesize turn 1", str(cm.exception))

    def test_generate_audio_empty_script_raises_error(self):
        """Test that empty script raises AudioGenerationError."""
        generator = self._make_generator()

        with self.assertRaises(AudioGenerationError) as cm:
            generator.generate_audio("")

        self.assertIn("Script too short or empty", str(cm.exception))

    def test_generate_audio_short_script_raises_error(self):
        """Test that a very short script raises AudioGenerationError."""
        generator = self._make_generator()

        with self.assertRaises(AudioGenerationError) as cm:
            generator.generate_audio("Short script.")

        self.assertIn("Script too short or empty", str(cm.exception))

    def test_generate_audio_no_turns_raises_error(self):
        """Test that a script with no speakable turns raises AudioGenerationError."""
        generator = self._make_generator()
        script = "# Just a header\n" + "**Bold text only**\n" * 10

        with self.assertRaises(AudioGenerationError) as cm:
            generator.generate_audio(script)

        self.assertIn("No speakable turns found", str(cm.exception))

    def test_generate_audio_success(self):
        """Test that generate_audio parses turns, synthesizes, and returns AudioResult."""
        generator = self._make_generator()

        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI.
Alex: That's right. The latest developments are fascinating.
Sam: Absolutely. Let's dive into the details."""

        pcm = b"\x00\x01" * 24000  # 1 second of fake 24kHz PCM

        # Mock(name=...) sets the repr name, not the .name attribute — set it directly.
        mock_file = Mock()
        mock_file.name = "/tmp/test_episode.wav"
        mock_ntf = Mock()
        mock_ntf.__enter__ = Mock(return_value=mock_file)
        mock_ntf.__exit__ = Mock(return_value=False)

        with (
            patch.object(generator, "_synthesize_turns", return_value=pcm) as mock_synth,
            patch("wave.open"),
            patch.object(generator, "convert_wav_to_mp3"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.stat", return_value=Mock(st_size=2048)),
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink"),
            patch("tempfile.NamedTemporaryFile", return_value=mock_ntf),
        ):
            result = generator.generate_audio(script)

        mock_synth.assert_called_once()
        self.assertIsInstance(result, AudioResult)

    def test_get_available_voices_structure(self):
        """Test get_available_voices returns expected structure."""
        generator = self._make_generator()
        voices = generator.get_available_voices()

        self.assertIsInstance(voices, dict)
        self.assertIn("male", voices)
        self.assertIn("female", voices)
        self.assertIn("Puck", voices["male"])
        self.assertIn("Kore", voices["female"])

    def test_get_available_voices_returns_copy(self):
        """Test that get_available_voices returns a copy, not the class dict."""
        generator = self._make_generator()
        voices = generator.get_available_voices()
        voices["male"].append("Hacked")

        self.assertNotIn("Hacked", AudioGenerator.AVAILABLE_VOICES["male"])

    def test_convert_wav_to_mp3(self):
        """Test WAV to MP3 conversion via pydub."""
        import sys

        generator = self._make_generator()
        wav_path = Path("/test/input.wav")
        mp3_path = Path("/test/output.mp3")

        mock_segment = Mock()
        mock_audio_segment = Mock()
        mock_audio_segment.from_wav.return_value = mock_segment
        mock_pydub = Mock()
        mock_pydub.AudioSegment = mock_audio_segment

        # Patch sys.modules so the local `from pydub import AudioSegment` resolves
        # to our mock — avoids audioop import failure on Python 3.13+.
        with patch.dict(sys.modules, {"pydub": mock_pydub}):
            generator.convert_wav_to_mp3(wav_path, mp3_path)

        mock_audio_segment.from_wav.assert_called_once_with(wav_path)
        mock_segment.export.assert_called_once_with(mp3_path, format="mp3")


if __name__ == "__main__":
    unittest.main()
