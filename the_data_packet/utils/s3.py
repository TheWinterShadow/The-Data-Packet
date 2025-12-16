"""AWS S3 storage backend."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from the_data_packet.core.config import get_config
from the_data_packet.core.exceptions import ConfigurationError, NetworkError
from the_data_packet.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class S3UploadResult:
    """Result of S3 upload operation."""

    success: bool
    s3_url: Optional[str] = None
    error_message: Optional[str] = None
    file_size_bytes: Optional[int] = None


class S3Storage:
    """AWS S3 storage backend."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name (defaults to config)
            aws_access_key_id: AWS access key (defaults to config/env)
            aws_secret_access_key: AWS secret key (defaults to config/env)
            region: AWS region (defaults to config)
        """
        config = get_config()

        self.bucket_name = bucket_name or config.s3_bucket_name
        if not self.bucket_name:
            raise ConfigurationError("S3 bucket name is required")

        self.region = region or config.aws_region

        # Initialize S3 client
        try:
            session_kwargs = {"region_name": self.region}

            # Use provided credentials if available
            if aws_access_key_id and aws_secret_access_key:
                session_kwargs.update(
                    {
                        "aws_access_key_id": aws_access_key_id,
                        "aws_secret_access_key": aws_secret_access_key,
                    }
                )

            self.s3_client = boto3.client("s3", **session_kwargs)

            # Test credentials
            self._test_credentials()

        except NoCredentialsError:
            raise ConfigurationError(
                "AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY "
                "environment variables or configure AWS CLI."
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize S3 client: {e}")

        logger.info(f"Initialized S3 storage for bucket: {self.bucket_name}")

    def upload_file(
        self,
        local_path: Path,
        s3_key: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> S3UploadResult:
        """
        Upload a file to S3.

        Args:
            local_path: Path to local file
            s3_key: S3 object key (defaults to filename)
            public: Whether to make the file publicly readable
            content_type: MIME type for the file

        Returns:
            S3UploadResult with upload details
        """
        if not local_path.exists():
            return S3UploadResult(
                success=False, error_message=f"File not found: {local_path}"
            )

        if s3_key is None:
            s3_key = local_path.name

        logger.info(f"Uploading {local_path} to s3://{self.bucket_name}/{s3_key}")

        try:
            file_size = local_path.stat().st_size

            # Prepare upload arguments
            upload_args: Dict[str, Any] = {
                "Filename": str(local_path),
                "Bucket": self.bucket_name,
                "Key": s3_key,
            }

            # Add content type if specified
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            if extra_args:
                upload_args["ExtraArgs"] = extra_args

            # Upload file
            self.s3_client.upload_file(**upload_args)

            # Generate S3 URL
            s3_url = (
                f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            )

            logger.info(f"Upload successful: {s3_url}")

            return S3UploadResult(
                success=True,
                s3_url=s3_url,
                file_size_bytes=file_size,
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = f"S3 upload failed ({error_code}): {e}"
            logger.error(error_message)

            return S3UploadResult(
                success=False,
                error_message=error_message,
            )
        except Exception as e:
            error_message = f"Upload failed: {e}"
            logger.error(error_message)

            return S3UploadResult(
                success=False,
                error_message=error_message,
            )

    def _test_credentials(self) -> None:
        """Test S3 credentials by listing buckets."""
        try:
            self.s3_client.list_buckets()
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "AccessDenied":
                raise ConfigurationError(
                    "AWS credentials are invalid or lack permissions"
                )
            elif error_code == "SignatureDoesNotMatch":
                raise ConfigurationError("AWS secret access key is incorrect")
            else:
                raise ConfigurationError(f"AWS credentials test failed: {e}")
        except Exception as e:
            raise NetworkError(f"Failed to test AWS credentials: {e}")

    def bucket_exists(self) -> bool:
        """Check if the configured bucket exists and is accessible."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code in ["404", "NoSuchBucket"]:
                logger.warning(f"Bucket {self.bucket_name} does not exist")
                return False
            elif error_code == "403":
                logger.warning(f"No access to bucket {self.bucket_name}")
                return False
            else:
                logger.error(f"Error checking bucket {self.bucket_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"Failed to check bucket {self.bucket_name}: {e}")
            return False
