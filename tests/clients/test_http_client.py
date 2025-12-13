"""Tests for http_client module."""

import unittest
from unittest.mock import Mock, patch, MagicMock

from the_data_packet.clients.http_client import HTTPClient


class TestHTTPClient(unittest.TestCase):
    """Test cases for HTTPClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = HTTPClient()

    def test_initialization(self):
        """Test HTTPClient initialization."""
        self.assertIsNone(self.client.session)
        self.assertEqual(self.client.timeout, 30)
        self.assertIsNotNone(self.client.headers)

    def test_initialization_with_custom_timeout(self):
        """Test HTTPClient initialization with custom timeout."""
        client = HTTPClient(timeout=60)
        self.assertEqual(client.timeout, 60)

    def test_initialization_with_custom_headers(self):
        """Test HTTPClient initialization with custom headers."""
        custom_headers = {'Custom-Header': 'test-value'}
        client = HTTPClient(headers=custom_headers)
        self.assertEqual(client.headers['Custom-Header'], 'test-value')

    @patch('requests.Session')
    def test_get_session_creation(self, mock_session_class):
        """Test session creation."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        session = self.client._get_session()

        self.assertEqual(session, mock_session)
        self.assertEqual(self.client.session, mock_session)
        mock_session_class.assert_called_once()

    @patch('requests.Session')
    def test_get_session_reuse(self, mock_session_class):
        """Test session reuse when already created."""
        mock_session = Mock()
        self.client.session = mock_session

        session = self.client._get_session()

        self.assertEqual(session, mock_session)
        mock_session_class.assert_not_called()

    @patch('requests.Session')
    def test_get_success(self, mock_session_class):
        """Test successful GET request."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "Response content"
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        response = self.client.get("https://example.com")

        self.assertEqual(response, mock_response)
        mock_session.get.assert_called_once_with(
            "https://example.com",
            timeout=30,
            headers=self.client.headers
        )

    @patch('requests.Session')
    def test_get_with_custom_params(self, mock_session_class):
        """Test GET request with custom parameters."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        params = {'param1': 'value1'}
        custom_headers = {'Custom': 'header'}

        response = self.client.get(
            "https://example.com",
            params=params,
            headers=custom_headers,
            timeout=60
        )

        mock_session.get.assert_called_once_with(
            "https://example.com",
            params=params,
            timeout=60,
            headers=custom_headers
        )

    @patch('requests.Session')
    def test_get_http_error(self, mock_session_class):
        """Test GET request handles HTTP errors."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        with self.assertRaises(Exception) as cm:
            self.client.get("https://example.com")

        self.assertIn("HTTP Error", str(cm.exception))

    @patch('requests.Session')
    def test_post_success(self, mock_session_class):
        """Test successful POST request."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        data = {'key': 'value'}
        response = self.client.post("https://example.com", data=data)

        self.assertEqual(response, mock_response)
        mock_session.post.assert_called_once_with(
            "https://example.com",
            data=data,
            timeout=30,
            headers=self.client.headers
        )

    @patch('requests.Session')
    def test_post_with_json(self, mock_session_class):
        """Test POST request with JSON data."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        json_data = {'key': 'value'}
        response = self.client.post("https://example.com", json=json_data)

        mock_session.post.assert_called_once_with(
            "https://example.com",
            json=json_data,
            timeout=30,
            headers=self.client.headers
        )

    def test_close_with_session(self):
        """Test closing client with active session."""
        mock_session = Mock()
        self.client.session = mock_session

        self.client.close()

        mock_session.close.assert_called_once()
        self.assertIsNone(self.client.session)

    def test_close_without_session(self):
        """Test closing client without active session."""
        # Should not raise any exceptions
        self.client.close()
        self.assertIsNone(self.client.session)

    def test_context_manager(self):
        """Test HTTPClient as context manager."""
        with patch.object(self.client, 'close') as mock_close:
            with self.client as client:
                self.assertEqual(client, self.client)

            mock_close.assert_called_once()

    def test_default_headers(self):
        """Test default headers are set correctly."""
        expected_headers = {
            'User-Agent': 'the-data-packet/2.0.0'
        }

        for key, value in expected_headers.items():
            self.assertEqual(self.client.headers[key], value)


if __name__ == '__main__':
    unittest.main()
