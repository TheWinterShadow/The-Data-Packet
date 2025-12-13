"""Tests for CLI module."""

import unittest
from unittest.mock import MagicMock, patch, call
import sys
from io import StringIO
from pathlib import Path

from the_data_packet.cli import main


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        """Clean up after tests."""
        sys.argv = self.original_argv

    @patch('sys.stderr', new_callable=StringIO)
    def test_help_output(self, mock_stderr):
        """Test that help output is displayed correctly."""
        sys.argv = ['cli.py', '--help']
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)

    @patch('the_data_packet.cli.PodcastPipeline')
    @patch('the_data_packet.cli.setup_logging')
    def test_default_configuration(self, mock_setup_logging, mock_pipeline_class):
        """Test default CLI configuration."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.articles_scraped = 2
        mock_result.script_generated = True
        mock_result.audio_generated = True
        mock_result.execution_time_seconds = 10.5
        mock_pipeline.run.return_value = mock_result

        sys.argv = ['cli.py', '--quiet']
        main()

        mock_setup_logging.assert_called_once_with(level='ERROR')
        mock_pipeline_class.assert_called_once()
        mock_pipeline.run.assert_called_once()

    @patch('sys.stderr', new_callable=StringIO)
    def test_audio_only_without_script_file(self, mock_stderr):
        """Test audio-only mode without script file fails."""
        sys.argv = ['cli.py', '--audio-only']
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)
        self.assertIn('--script-file is required', mock_stderr.getvalue())

    @patch('builtins.open')
    @patch('pathlib.Path.exists')
    @patch('the_data_packet.audio.GeminiTTSGenerator')
    def test_audio_only_mode(self, mock_tts_class, mock_exists, mock_open):
        """Test audio-only mode with valid script file."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'test script'
        mock_tts = MagicMock()
        mock_tts_class.return_value = mock_tts
        mock_result = MagicMock()
        mock_result.output_file = 'output.wav'
        mock_tts.generate_audio.return_value = mock_result

        sys.argv = ['cli.py', '--audio-only',
                    '--script-file', 'test.txt', '--quiet']
        main()

        mock_tts_class.assert_called_once()
        mock_tts.generate_audio.assert_called_once()


if __name__ == '__main__':
    unittest.main()
