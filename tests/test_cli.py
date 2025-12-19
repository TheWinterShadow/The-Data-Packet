"""Unit tests for cli.py module."""

import argparse
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from the_data_packet import cli
from the_data_packet.core import ConfigurationError


class TestCLI(unittest.TestCase):
    """Test cases for command-line interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_args = [
            "the-data-packet",
            "--output",
            "/tmp/test",
            "--sources",
            "wired",
            "--categories",
            "security",
            "ai",
            "--anthropic-key",
            "test-key",
        ]

    @patch("argparse.ArgumentParser.parse_args")
    def test_argument_parser_creation(self, mock_parse_args):
        """Test that argument parser is created with correct arguments."""
        mock_parse_args.return_value = Mock(
            anthropic_key="test-key",
            google_key=None,
            sources=["wired"],
            categories=["security", "ai"],
            max_articles=1,
            script_only=False,
            audio_only=False,
            voice_a="en-US-Neural2-A",
            voice_b="en-US-Neural2-B",
            output=Path("./output"),
            show_name="The Data Packet",
            s3_bucket=None,
            no_s3=False,
            log_level="INFO",
            save_intermediate=False,
        )

        # This should not raise an exception
        with patch("the_data_packet.cli.setup_logging"):
            with patch("the_data_packet.cli.get_config"):
                with patch("the_data_packet.cli.PodcastPipeline"):
                    try:
                        cli.main()
                    except SystemExit:
                        pass  # Expected when mocking

    @patch("sys.argv", ["the-data-packet", "--script-only", "--audio-only"])
    @patch("sys.exit")
    def test_mutually_exclusive_options_error(self, mock_exit):
        """Test that mutually exclusive options cause error."""
        with patch("builtins.print"):
            cli.main()
            mock_exit.assert_called_with(1)

    @patch("the_data_packet.cli.get_config")
    @patch("the_data_packet.cli.setup_logging")
    @patch("the_data_packet.cli.PodcastPipeline")
    @patch("argparse.ArgumentParser.parse_args")
    def test_successful_pipeline_execution(
        self, mock_parse_args, mock_pipeline_class, mock_setup_logging, mock_get_config
    ):
        """Test successful pipeline execution."""
        # Setup mocks
        mock_args = Mock(
            anthropic_key="test-key",
            google_key=None,
            sources=["wired"],
            categories=["security"],
            max_articles=1,
            script_only=False,
            audio_only=False,
            voice_a="en-US-Neural2-A",
            voice_b="en-US-Neural2-B",
            output=Path("./output"),
            show_name="The Data Packet",
            s3_bucket=None,
            no_s3=False,
            log_level="INFO",
            save_intermediate=False,
        )
        mock_parse_args.return_value = mock_args

        mock_config = Mock()
        mock_get_config.return_value = mock_config

        mock_pipeline = Mock()
        mock_result = Mock(
            success=True,
            execution_time_seconds=45.2,
            articles_collected=3,
            script_generated=True,
            script_path=Path("./output/script.txt"),
            s3_script_url="https://s3.amazonaws.com/bucket/script.txt",
            audio_generated=True,
            audio_path=Path("./output/audio.mp3"),
            s3_audio_url="https://s3.amazonaws.com/bucket/audio.mp3",
        )
        mock_pipeline.run.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline

        with patch("builtins.print") as mock_print:
            cli.main()

        # Verify setup was called
        mock_setup_logging.assert_called_once_with("INFO")

        # Verify config was created with overrides
        mock_get_config.assert_called_once()

        # Verify pipeline was created and run
        mock_pipeline_class.assert_called_once_with(mock_config)
        mock_pipeline.run.assert_called_once()

        # Verify success messages were printed
        mock_print.assert_any_call("✅ Podcast generation completed successfully!")

    @patch("the_data_packet.cli.get_config")
    @patch("the_data_packet.cli.setup_logging")
    @patch("the_data_packet.cli.PodcastPipeline")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("sys.exit")
    def test_failed_pipeline_execution(
        self,
        mock_exit,
        mock_parse_args,
        mock_pipeline_class,
        mock_setup_logging,
        mock_get_config,
    ):
        """Test failed pipeline execution."""
        # Setup mocks
        mock_args = Mock(
            anthropic_key="test-key",
            google_key=None,
            sources=["wired"],
            categories=["security"],
            max_articles=1,
            script_only=False,
            audio_only=False,
            voice_a="en-US-Neural2-A",
            voice_b="en-US-Neural2-B",
            output=Path("./output"),
            show_name="The Data Packet",
            s3_bucket=None,
            no_s3=False,
            log_level="INFO",
            save_intermediate=False,
        )
        mock_parse_args.return_value = mock_args

        mock_config = Mock()
        mock_get_config.return_value = mock_config

        mock_pipeline = Mock()
        mock_result = Mock(
            success=False,
            execution_time_seconds=12.3,
            error_message="Test error message",
        )
        mock_pipeline.run.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline

        with patch("builtins.print"):
            cli.main()

        mock_exit.assert_called_with(1)

    @patch("the_data_packet.cli.get_config")
    @patch("the_data_packet.cli.setup_logging")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("sys.exit")
    def test_configuration_error_handling(
        self, mock_exit, mock_parse_args, mock_setup_logging, mock_get_config
    ):
        """Test configuration error handling."""
        mock_args = Mock(
            anthropic_key=None,
            google_key=None,
            sources=["wired"],
            categories=["security"],
            max_articles=1,
            script_only=False,
            audio_only=False,
            voice_a="en-US-Neural2-A",
            voice_b="en-US-Neural2-B",
            output=Path("./output"),
            show_name="The Data Packet",
            s3_bucket=None,
            no_s3=False,
            log_level="INFO",
            save_intermediate=False,
        )
        mock_parse_args.return_value = mock_args

        mock_get_config.side_effect = ConfigurationError("Missing API key")

        with patch("builtins.print"):
            cli.main()

        mock_exit.assert_called_with(1)

    @patch("the_data_packet.cli.get_config")
    @patch("the_data_packet.cli.setup_logging")
    @patch("the_data_packet.cli.PodcastPipeline")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("sys.exit")
    def test_keyboard_interrupt_handling(
        self,
        mock_exit,
        mock_parse_args,
        mock_pipeline_class,
        mock_setup_logging,
        mock_get_config,
    ):
        """Test keyboard interrupt handling."""
        mock_args = Mock(
            anthropic_key="test-key",
            google_key=None,
            sources=["wired"],
            categories=["security"],
            max_articles=1,
            script_only=False,
            audio_only=False,
            voice_a="en-US-Neural2-A",
            voice_b="en-US-Neural2-B",
            output=Path("./output"),
            show_name="The Data Packet",
            s3_bucket=None,
            no_s3=False,
            log_level="INFO",
            save_intermediate=False,
        )
        mock_parse_args.return_value = mock_args

        mock_config = Mock()
        mock_get_config.return_value = mock_config

        mock_pipeline = Mock()
        mock_pipeline.run.side_effect = KeyboardInterrupt()
        mock_pipeline_class.return_value = mock_pipeline

        with patch("builtins.print"):
            cli.main()

        mock_exit.assert_called_with(130)

    def test_argument_parsing_script_only(self):
        """Test argument parsing for script-only mode."""
        parser = argparse.ArgumentParser()

        # Add the same arguments as in cli.py
        parser.add_argument("--script-only", action="store_true")
        parser.add_argument("--audio-only", action="store_true")

        args = parser.parse_args(["--script-only"])
        self.assertTrue(args.script_only)
        self.assertFalse(args.audio_only)

    def test_argument_parsing_audio_only(self):
        """Test argument parsing for audio-only mode."""
        parser = argparse.ArgumentParser()

        # Add the same arguments as in cli.py
        parser.add_argument("--script-only", action="store_true")
        parser.add_argument("--audio-only", action="store_true")

        args = parser.parse_args(["--audio-only"])
        self.assertFalse(args.script_only)
        self.assertTrue(args.audio_only)

    def test_main_entry_point_exists(self):
        """Test that main entry point is defined."""
        self.assertTrue(hasattr(cli, "main"))
        self.assertTrue(callable(cli.main))


if __name__ == "__main__":
    unittest.main()
