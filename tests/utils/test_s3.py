"""Unit tests for utils.s3 module."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from the_data_packet.core.exceptions import ConfigurationError, NetworkError
from the_data_packet.utils.s3 import S3Storage, S3UploadResult


class TestS3UploadResult(unittest.TestCase):
    """Test cases for S3UploadResult dataclass."""

    def test_s3_upload_result_creation_defaults(self):
        """Test S3UploadResult creation with defaults."""
        result = S3UploadResult(success=True)

        self.assertTrue(result.success)
        self.assertIsNone(result.s3_url)
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.file_size_bytes)

    def test_s3_upload_result_creation_with_all_fields(self):
        """Test S3UploadResult creation with all fields."""
        result = S3UploadResult(
            success=True,
            s3_url="https://s3.amazonaws.com/bucket/file.txt",
            error_message=None,
            file_size_bytes=1024,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.s3_url, "https://s3.amazonaws.com/bucket/file.txt")
        self.assertIsNone(result.error_message)
        self.assertEqual(result.file_size_bytes, 1024)

    def test_s3_upload_result_failure(self):
        """Test S3UploadResult for failed upload."""
        result = S3UploadResult(success=False, error_message="Upload failed")

        self.assertFalse(result.success)
        self.assertIsNone(result.s3_url)
        self.assertEqual(result.error_message, "Upload failed")


class TestS3Storage(unittest.TestCase):
    """Test cases for S3Storage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.s3_bucket_name = "test-bucket"
        self.mock_config.aws_region = "us-east-1"
        self.mock_config.aws_access_key_id = "test-access-key"
        self.mock_config.aws_secret_access_key = "test-secret-key"

    def test_init_missing_bucket_name_raises_error(self):
        """Test that missing bucket name raises ConfigurationError."""
        with patch("the_data_packet.utils.s3.get_config") as mock_get_config:
            mock_config_no_bucket = Mock()
            mock_config_no_bucket.s3_bucket_name = None
            mock_config_no_bucket.aws_region = "us-east-1"
            mock_get_config.return_value = mock_config_no_bucket

            with self.assertRaises(ConfigurationError) as cm:
                S3Storage()

            self.assertIn("S3 bucket name is required", str(cm.exception))

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_init_with_config_values(self, mock_boto3_client, mock_get_config):
        """Test S3Storage initialization with config values."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        # Mock successful credential test
        mock_s3_client.head_bucket.return_value = {}

        storage = S3Storage()

        self.assertEqual(storage.bucket_name, "test-bucket")
        self.assertEqual(storage.region, "us-east-1")
        mock_boto3_client.assert_called_once_with("s3", region_name="us-east-1")

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_init_with_custom_values(self, mock_boto3_client, mock_get_config):
        """Test S3Storage initialization with custom values."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        # Mock successful credential test
        mock_s3_client.head_bucket.return_value = {}

        storage = S3Storage(
            bucket_name="custom-bucket",
            aws_access_key_id="custom-access",
            aws_secret_access_key="custom-secret",
            region="us-west-2",
        )

        self.assertEqual(storage.bucket_name, "custom-bucket")
        self.assertEqual(storage.region, "us-west-2")
        mock_boto3_client.assert_called_once_with(
            "s3",
            region_name="us-west-2",
            aws_access_key_id="custom-access",
            aws_secret_access_key="custom-secret",
        )

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_init_no_credentials_error(self, mock_boto3_client, mock_get_config):
        """Test initialization with no credentials raises ConfigurationError."""
        mock_get_config.return_value = self.mock_config
        mock_boto3_client.side_effect = NoCredentialsError()

        with self.assertRaises(ConfigurationError) as cm:
            S3Storage()

        self.assertIn("AWS credentials not found", str(cm.exception))

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_init_boto3_exception(self, mock_boto3_client, mock_get_config):
        """Test initialization with boto3 exception raises ConfigurationError."""
        mock_get_config.return_value = self.mock_config
        mock_boto3_client.side_effect = Exception("Boto3 error")

        with self.assertRaises(ConfigurationError) as cm:
            S3Storage()

        self.assertIn("Failed to initialize S3 client", str(cm.exception))

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_upload_file_nonexistent_file(self, mock_boto3_client, mock_get_config):
        """Test uploading nonexistent file."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_s3_client.head_bucket.return_value = {}
        mock_boto3_client.return_value = mock_s3_client

        storage = S3Storage()

        nonexistent_path = Path("/nonexistent/file.txt")
        result = storage.upload_file(nonexistent_path)

        self.assertFalse(result.success)
        self.assertIn("File not found", result.error_message)

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_upload_file_success(self, mock_boto3_client, mock_get_config):
        """Test successful file upload."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.upload_file.return_value = None
        mock_boto3_client.return_value = mock_s3_client

        storage = S3Storage()

        # Create a temporary file for testing
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value = Mock(st_size=1024)

                test_path = Path("/tmp/test.txt")
                result = storage.upload_file(test_path, s3_key="test/file.txt")

                self.assertTrue(result.success)
                self.assertIn("test-bucket", result.s3_url)
                self.assertIn("test/file.txt", result.s3_url)
                self.assertEqual(result.file_size_bytes, 1024)

                # Verify S3 upload was called
                mock_s3_client.upload_file.assert_called_once()

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_upload_file_with_content_type(self, mock_boto3_client, mock_get_config):
        """Test file upload with custom content type."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.upload_file.return_value = None
        mock_boto3_client.return_value = mock_s3_client

        storage = S3Storage()

        # Create a temporary file for testing
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value = Mock(st_size=2048)

                test_path = Path("/tmp/test.json")
                result = storage.upload_file(
                    test_path, s3_key="data/test.json", content_type="application/json"
                )

                self.assertTrue(result.success)

                # Check that ExtraArgs were passed with ContentType
                call_args = mock_s3_client.upload_file.call_args
                self.assertIn("ExtraArgs", call_args[1])
                self.assertEqual(
                    call_args[1]["ExtraArgs"]["ContentType"], "application/json"
                )

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_upload_file_s3_error(self, mock_boto3_client, mock_get_config):
        """Test file upload with S3 error."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.upload_file.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "upload_file",
        )
        mock_boto3_client.return_value = mock_s3_client

        storage = S3Storage()

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value = Mock(st_size=1024)

                test_path = Path("/tmp/test.txt")
                result = storage.upload_file(test_path)

                self.assertFalse(result.success)
                self.assertIn("S3 upload failed", result.error_message)

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_upload_file_default_s3_key(self, mock_boto3_client, mock_get_config):
        """Test file upload with default S3 key (filename)."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_s3_client.list_buckets.return_value = {}  # Fix credential test
        mock_s3_client.upload_file.return_value = None
        mock_boto3_client.return_value = mock_s3_client

        storage = S3Storage()

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value = Mock(st_size=512)

                test_path = Path("/tmp/myfile.txt")
                result = storage.upload_file(test_path)  # No s3_key specified

                self.assertTrue(result.success)

                # Check that upload_file was called with correct arguments
                mock_s3_client.upload_file.assert_called_once()
                call_kwargs = mock_s3_client.upload_file.call_args.kwargs
                self.assertEqual(call_kwargs["Key"], "myfile.txt")
                self.assertEqual(call_kwargs["Bucket"], "test-bucket")

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_test_credentials_success(self, mock_boto3_client, mock_get_config):
        """Test successful credential testing."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_s3_client.head_bucket.return_value = {}
        mock_boto3_client.return_value = mock_s3_client

        # Should not raise an exception
        storage = S3Storage()
        self.assertIsNotNone(storage)

    @patch("the_data_packet.utils.s3.get_config")
    @patch("boto3.client")
    def test_test_credentials_failure(self, mock_boto3_client, mock_get_config):
        """Test credential testing failure."""
        mock_get_config.return_value = self.mock_config
        mock_s3_client = Mock()
        mock_s3_client.list_buckets.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "list_buckets",
        )
        mock_boto3_client.return_value = mock_s3_client

        with self.assertRaises(ConfigurationError) as cm:
            S3Storage()

        self.assertIn("AWS credentials are invalid", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
