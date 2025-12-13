"""Tests for audio modules."""

import unittest
from unittest.mock import MagicMock, patch, Mock, mock_open
from pathlib import Path

from the_data_packet.audio import GeminiTTSGenerator


class TestGeminiTTSGenerator(unittest.TestCase):
    """Test cases for the GeminiTTSGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.generator = GeminiTTSGenerator(
            api_key=self.api_key,
            voice_a="Puck",
            voice_b="Kore"
        )

    def test_initialization(self):
        """Test GeminiTTSGenerator initialization."""
        self.assertEqual(self.generator.api_key, self.api_key)
        self.assertEqual(self.generator.voice_a, "Puck")
        self.assertEqual(self.generator.voice_b, "Kore")

    def test_initialization_default_voices(self):
        """Test initialization with default voices."""
        generator = GeminiTTSGenerator(api_key="test-key")
        self.assertEqual(generator.voice_a, "Puck")
        self.assertEqual(generator.voice_b, "Kore")

    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        with self.assertRaises(ValueError):
            GeminiTTSGenerator(api_key=None)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_parse_script(self, mock_model_class, mock_configure):
        """Test script parsing functionality."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '[{"speaker": "Alex", "text": "Hello"}, {"speaker": "Sam", "text": "Hi"}]'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        script = "Alex: Hello\\nSam: Hi"
        result = self.generator._parse_script(script)

        expected = [
            {"speaker": "Alex", "text": "Hello"},
            {"speaker": "Sam", "text": "Hi"}
        ]
        self.assertEqual(result, expected)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_speech_segment(self, mock_model_class, mock_configure):
        """Test speech segment generation."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.candidates = [
            Mock(content=Mock(parts=[Mock(inline_data=Mock(data=b'audio_data'))]))]
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        segment = {"speaker": "Alex", "text": "Hello world"}
        result = self.generator._generate_speech_segment(segment)

        self.assertEqual(result, b'audio_data')
        mock_model.generate_content.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('wave.open')
    @patch.object(GeminiTTSGenerator, '_parse_script')
    @patch.object(GeminiTTSGenerator, '_generate_speech_segment')
    def test_generate_audio(self, mock_generate_segment, mock_parse_script, mock_wave_open, mock_file_open):
        """Test full audio generation process."""
        # Mock script parsing
        mock_parse_script.return_value = [
            {"speaker": "Alex", "text": "Hello"},
            {"speaker": "Sam", "text": "Hi"}
        ]

        # Mock speech generation
        mock_generate_segment.return_value = b'audio_data'

        # Mock wave file
        mock_wave_file = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wave_file

        script = "Alex: Hello\\nSam: Hi"
        output_path = Path("test_output.wav")

        result = self.generator.generate_audio(script, output_path)

        # Verify result
        self.assertEqual(result.output_file, output_path)
        self.assertTrue(result.success)

        # Verify methods were called
        mock_parse_script.assert_called_once_with(script)
        self.assertEqual(mock_generate_segment.call_count, 2)

    def test_voice_mapping(self):
        """Test voice mapping for different speakers."""
        # Test Alex voice mapping
        alex_voice = self.generator._get_voice_for_speaker("Alex")
        self.assertEqual(alex_voice, "Puck")

        # Test Sam voice mapping
        sam_voice = self.generator._get_voice_for_speaker("Sam")
        self.assertEqual(sam_voice, "Kore")

        # Test default voice mapping
        default_voice = self.generator._get_voice_for_speaker("Unknown")
        self.assertEqual(default_voice, "Puck")


if __name__ == '__main__':
    unittest.main()
