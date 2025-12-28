"""Tests for utils.loki module."""

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from the_data_packet.utils.loki import (
    JsonEncoder,
    LogUploadError,
    LokiUploader,
    upload_logs_to_loki,
)


class TestLogUploadError(unittest.TestCase):
    """Test cases for LogUploadError exception."""

    def test_log_upload_error_with_message_only(self):
        """Test LogUploadError with message only."""
        error = LogUploadError("Test error")
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.message, "Test error")
        self.assertIsNone(error.response)

    def test_log_upload_error_with_response(self):
        """Test LogUploadError with message and response."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        error = LogUploadError("Test error", response=mock_response)
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.response, mock_response)

    def test_log_upload_error_inheritance(self):
        """Test LogUploadError inherits from Exception."""
        error = LogUploadError("Test error")
        self.assertIsInstance(error, Exception)


class TestJsonEncoder(unittest.TestCase):
    """Test cases for JsonEncoder."""

    def test_json_encoder_datetime_encoding(self):
        """Test JsonEncoder encodes datetime objects."""
        encoder = JsonEncoder()
        test_datetime = datetime(2023, 12, 27, 12, 30, 45, tzinfo=timezone.utc)

        result = encoder.default(test_datetime)
        self.assertEqual(result, "2023-12-27T12:30:45+00:00")

    def test_json_encoder_datetime_encoding_naive(self):
        """Test JsonEncoder encodes naive datetime objects."""
        encoder = JsonEncoder()
        test_datetime = datetime(2023, 12, 27, 12, 30, 45)

        result = encoder.default(test_datetime)
        self.assertEqual(result, "2023-12-27T12:30:45")

    def test_json_encoder_other_objects_fallback(self):
        """Test JsonEncoder falls back to default for other objects."""
        # Test with unsupported object type
        with self.assertRaises(TypeError):
            JsonEncoder().default(set([1, 2, 3]))

    def test_json_encoder_full_serialization(self):
        """Test full JSON serialization with datetime objects."""
        test_data = {
            "timestamp": datetime(2023, 12, 27, 12, 30, 45, tzinfo=timezone.utc),
            "message": "Test log entry",
            "level": "INFO",
        }

        result = json.dumps(test_data, cls=JsonEncoder)
        expected = '{"timestamp": "2023-12-27T12:30:45+00:00", "message": "Test log entry", "level": "INFO"}'
        self.assertEqual(result, expected)


class TestLokiUploader(unittest.TestCase):
    """Test cases for LokiUploader."""

    def test_init_with_valid_parameters(self):
        """Test LokiUploader initialization with valid parameters."""
        uploader = LokiUploader(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
            service_name="test_service",
            environment="test",
            timeout=60,
        )

        self.assertEqual(uploader.url, "https://loki.example.com/loki/api/v1/push")
        self.assertEqual(uploader.user, "test_user")
        self.assertEqual(uploader.api_key, "test_key")
        self.assertEqual(uploader.service_name, "test_service")
        self.assertEqual(uploader.environment, "test")
        self.assertEqual(uploader.timeout, 60)

    def test_init_with_default_parameters(self):
        """Test LokiUploader initialization with default parameters."""
        uploader = LokiUploader(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
        )

        self.assertEqual(uploader.service_name, "the_data_packet")
        self.assertEqual(uploader.environment, "production")
        self.assertEqual(uploader.timeout, 30)

    def test_init_missing_url_raises_error(self):
        """Test LokiUploader initialization with missing URL."""
        with self.assertRaisesRegex(ValueError, "URL, user, and api_key are required"):
            LokiUploader(url="", user="test_user", api_key="test_key")

    def test_init_missing_user_raises_error(self):
        """Test LokiUploader initialization with missing user."""
        with self.assertRaisesRegex(ValueError, "URL, user, and api_key are required"):
            LokiUploader(
                url="https://loki.example.com/loki/api/v1/push",
                user="",
                api_key="test_key",
            )

    def test_init_missing_api_key_raises_error(self):
        """Test LokiUploader initialization with missing API key."""
        with self.assertRaisesRegex(ValueError, "URL, user, and api_key are required"):
            LokiUploader(
                url="https://loki.example.com/loki/api/v1/push",
                user="test_user",
                api_key="",
            )

    def test_init_none_values_raises_error(self):
        """Test LokiUploader initialization with None values."""
        with self.assertRaisesRegex(ValueError, "URL, user, and api_key are required"):
            LokiUploader(url=None, user="test_user", api_key="test_key")

    @patch("the_data_packet.utils.loki.requests.post")
    def test_upload_from_file_success(self, mock_post):
        """Test successful upload from file."""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # Create test log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            test_logs = [
                {
                    "timestamp": "2023-12-27T12:30:45Z",
                    "level": "INFO",
                    "message": "Test 1",
                },
                {
                    "timestamp": "2023-12-27T12:31:45Z",
                    "level": "ERROR",
                    "message": "Test 2",
                },
            ]
            for log in test_logs:
                f.write(json.dumps(log) + "\n")
            temp_path = Path(f.name)

        try:
            uploader = LokiUploader(
                url="https://loki.example.com/loki/api/v1/push",
                user="test_user",
                api_key="test_key",
            )

            result = uploader.upload_from_file(temp_path)
            self.assertEqual(result, 2)

            # Verify request was made
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            self.assertEqual(call_args[1]["auth"], ("test_user", "test_key"))
            self.assertEqual(call_args[1]["timeout"], 30)

        finally:
            temp_path.unlink()

    def test_upload_from_file_nonexistent_file(self):
        """Test upload from nonexistent file."""
        uploader = LokiUploader(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
        )

        with self.assertRaises(FileNotFoundError):
            uploader.upload_from_file(Path("nonexistent_file.jsonl"))

    @patch("the_data_packet.utils.loki.requests.post")
    def test_upload_from_file_empty_file(self, mock_post):
        """Test upload from empty file."""
        # Create empty test log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            temp_path = Path(f.name)

        try:
            uploader = LokiUploader(
                url="https://loki.example.com/loki/api/v1/push",
                user="test_user",
                api_key="test_key",
            )

            result = uploader.upload_from_file(temp_path)
            self.assertEqual(result, 0)

            # Verify no request was made
            mock_post.assert_not_called()

        finally:
            temp_path.unlink()

    @patch("the_data_packet.utils.loki.requests.post")
    def test_upload_from_file_http_error(self, mock_post):
        """Test upload from file with HTTP error."""
        # Setup mock response with error
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.text = "Internal Server Error"
        mock_response.json.side_effect = json.JSONDecodeError("No JSON", "", 0)
        mock_post.return_value = mock_response

        # Create test log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                '{"timestamp": "2023-12-27T12:30:45Z", "level": "INFO", "message": "Test"}\n'
            )
            temp_path = Path(f.name)

        try:
            uploader = LokiUploader(
                url="https://loki.example.com/loki/api/v1/push",
                user="test_user",
                api_key="test_key",
            )

            with self.assertRaises(LogUploadError) as exc_info:
                uploader.upload_from_file(temp_path)

            self.assertIn("HTTP 500: Internal Server Error", str(exc_info.exception))

        finally:
            temp_path.unlink()

    @patch("the_data_packet.utils.loki.requests.post")
    def test_upload_logs_success(self, mock_post):
        """Test successful upload of logs."""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        uploader = LokiUploader(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
        )

        test_logs = [
            {"timestamp": "2023-12-27T12:30:45Z", "level": "INFO", "message": "Test 1"},
            {
                "timestamp": "2023-12-27T12:31:45Z",
                "level": "ERROR",
                "message": "Test 2",
            },
        ]

        result = uploader.upload_logs(test_logs)
        self.assertEqual(result, 2)

        # Verify request was made
        mock_post.assert_called_once()

    def test_upload_logs_empty_list(self):
        """Test upload of empty logs list."""
        uploader = LokiUploader(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
        )

        result = uploader.upload_logs([])
        self.assertEqual(result, 0)

    def test_read_log_file_success(self):
        """Test reading JSONL file successfully."""
        # Create test log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            test_logs = [
                {
                    "timestamp": "2023-12-27T12:30:45Z",
                    "level": "INFO",
                    "message": "Test 1",
                },
                {
                    "timestamp": "2023-12-27T12:31:45Z",
                    "level": "ERROR",
                    "message": "Test 2",
                },
            ]
            for log in test_logs:
                f.write(json.dumps(log) + "\n")
            temp_path = Path(f.name)

        try:
            uploader = LokiUploader(
                url="https://loki.example.com/loki/api/v1/push",
                user="test_user",
                api_key="test_key",
            )

            logs = uploader._read_log_file(temp_path)
            self.assertEqual(len(logs), 2)
            self.assertEqual(logs[0]["message"], "Test 1")
            self.assertEqual(logs[1]["message"], "Test 2")

        finally:
            temp_path.unlink()

    def test_read_log_file_with_invalid_lines(self):
        """Test reading JSONL file with invalid JSON lines."""
        # Create test log file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"valid": "json"}\n')
            f.write("invalid json line\n")
            f.write('{"another": "valid"}\n')
            temp_path = Path(f.name)

        try:
            uploader = LokiUploader(
                url="https://loki.example.com/loki/api/v1/push",
                user="test_user",
                api_key="test_key",
            )

            # Should skip invalid lines and only load valid ones
            logs = uploader._read_log_file(temp_path)
            self.assertEqual(len(logs), 2)
            self.assertEqual(logs[0]["valid"], "json")
            self.assertEqual(logs[1]["another"], "valid")

        finally:
            temp_path.unlink()

    def test_format_logs_for_loki(self):
        """Test formatting logs for Loki."""
        uploader = LokiUploader(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
        )

        logs = [
            {
                "timestamp": "2023-12-27T12:30:45+00:00",
                "level": "INFO",
                "message": "Test message",
                "module": "test.module",
            }
        ]

        result = uploader._format_logs_for_loki(logs)

        # Should have one formatted log entry
        self.assertEqual(len(result), 1)
        timestamp, log_line = result[0]
        # Just verify it's a valid nanosecond timestamp (18-19 digits)
        self.assertGreaterEqual(len(timestamp), 18)
        self.assertTrue(timestamp.isdigit())

        # Log line should be JSON string
        parsed_log = json.loads(log_line)
        self.assertEqual(parsed_log["level"], "INFO")
        self.assertEqual(parsed_log["message"], "Test message")

    def test_format_logs_for_loki_with_invalid_timestamp(self):
        """Test formatting logs with invalid timestamp."""
        uploader = LokiUploader(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
        )

        logs = [
            {
                "timestamp": "invalid-timestamp",
                "level": "INFO",
                "message": "Test message",
            }
        ]

        # Should skip entries with invalid timestamps
        result = uploader._format_logs_for_loki(logs)
        self.assertEqual(len(result), 0)


class TestUploadLogsToLoki(unittest.TestCase):
    """Test cases for upload_logs_to_loki convenience function."""

    @patch("the_data_packet.utils.loki.LokiUploader")
    def test_upload_logs_to_loki_convenience_function(self, mock_uploader_class):
        """Test upload_logs_to_loki convenience function."""
        # Setup mock
        mock_uploader = Mock()
        mock_uploader.upload_from_file.return_value = 5
        mock_uploader_class.return_value = mock_uploader

        test_path = Path("/test/path.jsonl")
        result = upload_logs_to_loki(
            file_path=test_path,
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
            service_name="test_service",
            environment="test",
            timeout=60,
        )

        # Verify LokiUploader was created with correct parameters
        mock_uploader_class.assert_called_once_with(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
            service_name="test_service",
            environment="test",
            timeout=60,
        )

        # Verify upload_from_file was called
        mock_uploader.upload_from_file.assert_called_once_with(test_path)

        # Verify return value
        self.assertEqual(result, 5)

    @patch("the_data_packet.utils.loki.LokiUploader")
    def test_upload_logs_to_loki_with_defaults(self, mock_uploader_class):
        """Test upload_logs_to_loki with default parameters."""
        # Setup mock
        mock_uploader = Mock()
        mock_uploader.upload_from_file.return_value = 3
        mock_uploader_class.return_value = mock_uploader

        test_path = Path("/test/path.jsonl")
        result = upload_logs_to_loki(
            file_path=test_path,
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
        )

        # Verify LokiUploader was created with default parameters
        mock_uploader_class.assert_called_once_with(
            url="https://loki.example.com/loki/api/v1/push",
            user="test_user",
            api_key="test_key",
            service_name="the_data_packet",
            environment="production",
            timeout=30,
        )

        self.assertEqual(result, 3)


if __name__ == "__main__":
    unittest.main()
