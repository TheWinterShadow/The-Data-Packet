"""Tests for tts_generator module."""

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path

from the_data_packet.audio.tts_generator import GeminiTTSGenerator


class TestGeminiTTSGenerator(unittest.TestCase):
    """Test cases for GeminiTTSGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "AIza-test-key"
        self.voice_a = "Puck"
        self.voice_b = "Kore"

    def test_initialization_with_all_params(self):
        """Test GeminiTTSGenerator initialization with all parameters."""
        generator = GeminiTTSGenerator(
            api_key=self.api_key,
            voice_a=self.voice_a,
            voice_b=self.voice_b
        )

        self.assertEqual(generator.api_key, self.api_key)
        self.assertEqual(generator.voice_a, self.voice_a)
        self.assertEqual(generator.voice_b, self.voice_b)

    def test_initialization_with_defaults(self):
        """Test GeminiTTSGenerator initialization with default voices."""
        generator = GeminiTTSGenerator(api_key=self.api_key)

        self.assertEqual(generator.api_key, self.api_key)
        self.assertEqual(generator.voice_a, "Puck")
        self.assertEqual(generator.voice_b, "Kore")

    def test_initialization_without_api_key(self):
        """Test GeminiTTSGenerator initialization fails without API key."""
        with self.assertRaises(ValueError) as cm:
            GeminiTTSGenerator(api_key=None)

        self.assertIn("Google API key is required", str(cm.exception))

    def test_initialization_empty_api_key(self):
        """Test GeminiTTSGenerator initialization fails with empty API key."""
        with self.assertRaises(ValueError) as cm:
            GeminiTTSGenerator(api_key="")

        self.assertIn("Google API key is required", str(cm.exception))

    def test_get_voice_for_speaker_alex(self):
        """Test voice mapping for Alex."""
        generator = GeminiTTSGenerator(
            api_key=self.api_key,
            voice_a="Charon",
            voice_b="Aoede"
        )

        voice = generator._get_voice_for_speaker("Alex")
        self.assertEqual(voice, "Charon")

    def test_get_voice_for_speaker_sam(self):
        """Test voice mapping for Sam."""
        generator = GeminiTTSGenerator(
            api_key=self.api_key,
            voice_a="Charon",
            voice_b="Aoede"
        )

        voice = generator._get_voice_for_speaker("Sam")
        self.assertEqual(voice, "Aoede")

    def test_get_voice_for_speaker_unknown(self):
        """Test voice mapping for unknown speaker defaults to voice_a."""
        generator = GeminiTTSGenerator(
            api_key=self.api_key,
            voice_a="Charon",
            voice_b="Aoede"
        )

        voice = generator._get_voice_for_speaker("Unknown")
        self.assertEqual(voice, "Charon")

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_parse_script_success(self, mock_model_class, mock_configure):
        """Test successful script parsing."""
        # Setup mock
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '[{"speaker": "Alex", "text": "Hello world"}, {"speaker": "Sam", "text": "Hi there"}]'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        generator = GeminiTTSGenerator(api_key=self.api_key)
        script = "Alex: Hello world\\nSam: Hi there"

        result = generator._parse_script(script)

        expected = [
            {"speaker": "Alex", "text": "Hello world"},
            {"speaker": "Sam", "text": "Hi there"}
        ]
        self.assertEqual(result, expected)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_speech_segment_success(self, mock_model_class, mock_configure):
        """Test successful speech segment generation."""
        # Setup mock
        mock_model = Mock()
        mock_response = Mock()
        mock_candidate = Mock()
        mock_part = Mock()
        mock_part.inline_data.data = b'audio_data_bytes'
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        generator = GeminiTTSGenerator(api_key=self.api_key)
        segment = {"speaker": "Alex", "text": "Hello world"}

        result = generator._generate_speech_segment(segment)

        self.assertEqual(result, b'audio_data_bytes')

    @patch('builtins.open', new_callable=mock_open)
    @patch('wave.open')
    @patch.object(GeminiTTSGenerator, '_parse_script')
    @patch.object(GeminiTTSGenerator, '_generate_speech_segment')
    def test_generate_audio_success(self, mock_generate_segment, mock_parse_script, mock_wave_open, mock_file_open):
        """Test successful audio generation."""
        # Setup mocks
        mock_parse_script.return_value = [
            {"speaker": "Alex", "text": "Hello"},
            {"speaker": "Sam", "text": "Hi"}
        ]
        mock_generate_segment.return_value = b'audio_data'

        mock_wave_file = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave_file

        generator = GeminiTTSGenerator(api_key=self.api_key)
        script = "Alex: Hello\\nSam: Hi"
        output_path = Path("test_output.wav")

        result = generator.generate_audio(script, output_path)

        # Verify result
        self.assertEqual(result.output_file, output_path)
        self.assertTrue(result.success)

        # Verify methods were called
        mock_parse_script.assert_called_once_with(script)
        self.assertEqual(mock_generate_segment.call_count, 2)

    @patch.object(GeminiTTSGenerator, '_parse_script')
    def test_generate_audio_parse_error(self, mock_parse_script):
        """Test audio generation handles parsing errors."""
        mock_parse_script.side_effect = Exception("Parse error")

        generator = GeminiTTSGenerator(api_key=self.api_key)
        script = "Invalid script"
        output_path = Path("test_output.wav")

        result = generator.generate_audio(script, output_path)

        self.assertFalse(result.success)
        self.assertIn("Parse error", result.error_message)

    def test_generate_audio_empty_script(self):
        """Test audio generation with empty script."""
        generator = GeminiTTSGenerator(api_key=self.api_key)

        with self.assertRaises(ValueError) as cm:
            generator.generate_audio("", Path("output.wav"))

        self.assertIn("Script content cannot be empty", str(cm.exception))

    def test_generate_audio_none_script(self):
        """Test audio generation with None script."""
        generator = GeminiTTSGenerator(api_key=self.api_key)

        with self.assertRaises(ValueError) as cm:
            generator.generate_audio(None, Path("output.wav"))

        self.assertIn("Script content cannot be empty", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
