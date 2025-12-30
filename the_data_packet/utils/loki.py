"""
Log upload utility for sending logs to Grafana Loki.

This module provides classes and functions for uploading structured logs
from JSONL files to Grafana Loki for centralized log aggregation and analysis.

Classes:
    LokiUploader: Main class for uploading logs to Grafana Loki
    LogUploadError: Custom exception for upload failures
    JsonEncoder: JSON encoder with datetime support

Functions:
    upload_logs_to_loki: Convenience function for one-time log uploads

Example:
    >>> from the_data_packet.utils.log_upload import LokiUploader
    >>>
    >>> uploader = LokiUploader(
    ...     url="https://logs-prod.grafana.net/loki/api/v1/push",
    ...     user="your_user_id",
    ...     api_key="your_api_key"
    ... )
    >>>
    >>> uploader.upload_from_file("/path/to/logs.jsonl")
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class LogUploadError(Exception):
    """Exception raised for log upload errors.

    Attributes:
        message: Explanation of the error
        response: Optional HTTP response object if applicable
    """

    def __init__(self, message: str, response: Optional[requests.Response] = None):
        """Initialize LogUploadError.

        Args:
            message: Error message describing what went wrong
            response: Optional HTTP response object for debugging
        """
        self.message = message
        self.response = response
        super().__init__(self.message)


class JsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects and other Python types.

    This encoder extends the default JSON encoder to handle datetime objects
    by converting them to ISO format strings.
    """

    def default(self, o: Any) -> Any:
        """Encode special Python objects to JSON-serializable formats.

        Args:
            obj: Object to encode

        Returns:
            JSON-serializable representation of the object

        Raises:
            TypeError: If object type is not serializable
        """
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class LokiUploader:
    """A class for uploading logs to Grafana Loki.

    This class provides methods to upload structured logs from JSONL files
    to Grafana Loki for centralized log management and analysis.

    Attributes:
        url: The Loki push API endpoint URL
        user: Username for authentication
        api_key: API key for authentication
        service_name: Default service name for log streams
        environment: Default environment for log streams
        timeout: Default timeout for HTTP requests in seconds

    Example:
        >>> uploader = LokiUploader(
        ...     url="https://logs-prod.grafana.net/loki/api/v1/push",
        ...     user="your_user_id",
        ...     api_key="your_api_key"
        ... )
        >>> uploader.upload_from_file("/path/to/logs.jsonl")
    """

    def __init__(
        self,
        url: str,
        user: str,
        api_key: str,
        service_name: str = "the_data_packet",
        environment: str = "production",
        timeout: int = 30,
    ):
        """Initialize the LokiUploader.

        Args:
            url: Loki push API endpoint URL
            user: Username for authentication
            api_key: API key for authentication
            service_name: Default service name for log streams
            environment: Default environment for log streams
            timeout: Default timeout for HTTP requests in seconds

        Raises:
            ValueError: If any required parameter is empty or None
        """
        if not all([url, user, api_key]):
            raise ValueError("URL, user, and api_key are required")

        self.url = url
        self.user = user
        self.api_key = api_key
        self.service_name = service_name
        self.environment = environment
        self.timeout = timeout

        logger.debug(f"LokiUploader initialized for {url}")

    def upload_from_file(
        self,
        file_path: Path,
        service_name: Optional[str] = None,
        environment: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> int:
        """Upload logs from a JSONL file to Loki.

        Args:
            file_path: Path to the JSONL log file
            service_name: Override default service name
            environment: Override default environment
            timeout: Override default timeout

        Returns:
            Number of log entries successfully uploaded

        Raises:
            FileNotFoundError: If the log file doesn't exist
            ValueError: If the file contains invalid JSON
            LogUploadError: If the upload fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")

        # Use provided values or fall back to instance defaults
        svc_name = service_name or self.service_name
        env = environment or self.environment
        req_timeout = timeout or self.timeout

        try:
            # Read and parse log file
            logs = self._read_log_file(file_path)
            if not logs:
                logger.warning(f"No logs found in {file_path}")
                return 0

            # Format logs for Loki
            formatted_logs = self._format_logs_for_loki(logs)

            # Create payload
            payload = self._create_loki_payload(formatted_logs, svc_name, env)

            # Send to Loki
            self._send_logs_to_loki(payload, req_timeout)

            logger.info(f"Successfully uploaded {len(logs)} logs to Loki")
            return len(logs)

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON in log file: {e}")
        except requests.RequestException as e:
            raise LogUploadError(f"Failed to upload logs: {e}")
        except Exception as e:
            raise LogUploadError(f"Unexpected error during log upload: {e}")

    def upload_logs(
        self,
        logs: List[Dict[str, Any]],
        service_name: Optional[str] = None,
        environment: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> int:
        """Upload logs directly from a list of dictionaries.

        Args:
            logs: List of log entries as dictionaries
            service_name: Override default service name
            environment: Override default environment
            timeout: Override default timeout

        Returns:
            Number of log entries successfully uploaded

        Raises:
            ValueError: If logs list is empty or contains invalid data
            LogUploadError: If the upload fails
        """
        if not logs:
            logger.warning("No logs provided for upload")
            return 0

        # Use provided values or fall back to instance defaults
        svc_name = service_name or self.service_name
        env = environment or self.environment
        req_timeout = timeout or self.timeout

        try:
            # Format logs for Loki
            formatted_logs = self._format_logs_for_loki(logs)

            # Create payload
            payload = self._create_loki_payload(formatted_logs, svc_name, env)

            # Send to Loki
            self._send_logs_to_loki(payload, req_timeout)

            logger.info(f"Successfully uploaded {len(logs)} logs to Loki")
            return len(logs)

        except requests.RequestException as e:
            raise LogUploadError(f"Failed to upload logs: {e}")
        except Exception as e:
            raise LogUploadError(f"Unexpected error during log upload: {e}")

    def _read_log_file(self, log_file: Path) -> List[Dict[str, Any]]:
        """Read and parse JSONL log file.

        Args:
            log_file: Path to the log file

        Returns:
            List of parsed log entries

        Raises:
            ValueError: If file contains invalid JSON
        """
        logs = []

        with open(log_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)
                    logs.append(log_entry)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON at line {line_num}: {e}")
                    continue

        return logs

    def _format_logs_for_loki(self, logs: List[Dict[str, Any]]) -> List[List[str]]:
        """Format logs for Loki ingestion.

        Args:
            logs: List of log entries

        Returns:
            List of formatted log entries as [timestamp, json_string] pairs
        """
        formatted_logs = []

        for log in logs:
            try:
                # Parse and normalize timestamp
                if "timestamp" in log:
                    if isinstance(log["timestamp"], str):
                        timestamp = datetime.fromisoformat(log["timestamp"]).replace(
                            tzinfo=timezone.utc
                        )
                    elif isinstance(log["timestamp"], datetime):
                        timestamp = log["timestamp"].replace(tzinfo=timezone.utc)
                    else:
                        timestamp = datetime.now(timezone.utc)
                else:
                    timestamp = datetime.now(timezone.utc)

                log["timestamp"] = timestamp

                # Convert to nanosecond timestamp for Loki
                nano_timestamp = str(int(timestamp.timestamp() * 1e9))
                log_json = json.dumps(log, cls=JsonEncoder)

                formatted_logs.append([nano_timestamp, log_json])

            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping log entry with invalid timestamp: {e}")
                continue

        return formatted_logs

    def _create_loki_payload(
        self, logs: List[List[str]], service_name: str, environment: str
    ) -> Dict[str, Any]:
        """Create Loki API payload.

        Args:
            logs: Formatted log entries
            service_name: Service name for the stream
            environment: Environment for the stream

        Returns:
            Loki API payload dictionary
        """
        return {
            "streams": [
                {
                    "stream": {
                        "service_name": service_name,
                        "environment": environment,
                        "trace_id": str(uuid.uuid4()),
                    },
                    "values": logs,
                }
            ]
        }

    def _send_logs_to_loki(self, payload: Dict[str, Any], timeout: int) -> None:
        """Send logs to Loki via HTTP POST.

        Args:
            payload: Loki API payload
            timeout: Request timeout in seconds

        Raises:
            LogUploadError: If the HTTP request fails
        """
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            url=self.url,
            auth=(self.user, self.api_key),
            json=payload,
            headers=headers,
            timeout=timeout,
        )

        # Check for HTTP errors
        if not response.ok:
            error_msg = f"HTTP {response.status_code}: {response.reason}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except json.JSONDecodeError:
                error_msg += f" - {response.text}"

            raise LogUploadError(error_msg, response)


def upload_logs_to_loki(
    file_path: Path,
    url: str,
    user: str,
    api_key: str,
    service_name: str = "the_data_packet",
    environment: str = "production",
    timeout: int = 30,
) -> int:
    """Convenience function for uploading logs to Loki.

    This is a simple wrapper around the LokiUploader class for one-time
    log uploads without needing to instantiate the class.

    Args:
        file_path: Path to the JSONL log file
        url: Loki push API endpoint URL
        user: Username for authentication
        api_key: API key for authentication
        service_name: Service name label for the logs
        environment: Environment label for the logs
        timeout: Request timeout in seconds

    Returns:
        Number of log entries successfully uploaded

    Raises:
        LogUploadError: If log upload fails
        FileNotFoundError: If the log file doesn't exist
        ValueError: If the file contains invalid JSON or missing parameters

    Example:
        >>> count = upload_logs_to_loki(
        ...     file_path="/path/to/logs.jsonl",
        ...     url="https://logs-prod.grafana.net/loki/api/v1/push",
        ...     user="your_user_id",
        ...     api_key="your_api_key"
        ... )
        >>> print(f"Uploaded {count} log entries")
    """
    uploader = LokiUploader(
        url=url,
        user=user,
        api_key=api_key,
        service_name=service_name,
        environment=environment,
        timeout=timeout,
    )

    return uploader.upload_from_file(file_path)
