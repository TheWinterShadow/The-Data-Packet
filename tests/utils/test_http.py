"""Unit tests for utils.http module."""

import unittest
from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

from the_data_packet.core.exceptions import NetworkError
from the_data_packet.utils.http import HTTPClient


class TestHTTPClient(unittest.TestCase):
    """Test cases for HTTPClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.http_timeout = 30
        self.mock_config.user_agent = "Test User Agent"

    @patch("the_data_packet.core.config.get_config")
    def test_init_with_defaults(self, mock_get_config):
        """Test HTTPClient initialization with default configuration."""
        mock_get_config.return_value = self.mock_config

        client = HTTPClient()

        self.assertEqual(client.timeout, 30)
        self.assertEqual(client.user_agent, "Test User Agent")
        self.assertIsInstance(client.session, requests.Session)

    @patch("the_data_packet.core.config.get_config")
    def test_init_with_custom_values(self, mock_get_config):
        """Test HTTPClient initialization with custom values."""
        mock_get_config.return_value = self.mock_config

        client = HTTPClient(timeout=60, user_agent="Custom Agent")

        self.assertEqual(client.timeout, 60)
        self.assertEqual(client.user_agent, "Custom Agent")

    @patch("the_data_packet.core.config.get_config")
    def test_session_headers_set(self, mock_get_config):
        """Test that session headers are properly configured."""
        mock_get_config.return_value = self.mock_config

        client = HTTPClient()

        # Check that important headers are set
        self.assertEqual(client.session.headers["User-Agent"], "Test User Agent")
        self.assertIn("Accept", client.session.headers)
        self.assertIn("Accept-Language", client.session.headers)
        self.assertIn("Accept-Encoding", client.session.headers)
        self.assertIn("Connection", client.session.headers)

    @patch("the_data_packet.core.config.get_config")
    @patch("requests.Session.get")
    def test_get_success(self, mock_session_get, mock_get_config):
        """Test successful GET request."""
        mock_get_config.return_value = self.mock_config

        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session_get.return_value = mock_response

        client = HTTPClient()
        response = client.get("https://example.com")

        self.assertEqual(response, mock_response)
        mock_session_get.assert_called_once_with("https://example.com", timeout=30)
        mock_response.raise_for_status.assert_called_once()

    @patch("the_data_packet.core.config.get_config")
    @patch("requests.Session.get")
    def test_get_with_custom_timeout(self, mock_session_get, mock_get_config):
        """Test GET request with custom timeout."""
        mock_get_config.return_value = self.mock_config

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session_get.return_value = mock_response

        client = HTTPClient()
        client.get("https://example.com", timeout=45)

        mock_session_get.assert_called_once_with("https://example.com", timeout=45)

    @patch("the_data_packet.core.config.get_config")
    @patch("requests.Session.get")
    def test_get_with_additional_kwargs(self, mock_session_get, mock_get_config):
        """Test GET request with additional keyword arguments."""
        mock_get_config.return_value = self.mock_config

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session_get.return_value = mock_response

        client = HTTPClient()
        client.get("https://example.com", headers={"Custom": "Header"})

        mock_session_get.assert_called_once_with(
            "https://example.com", timeout=30, headers={"Custom": "Header"}
        )

    @patch("the_data_packet.core.config.get_config")
    @patch("requests.Session.get")
    def test_get_request_exception(self, mock_session_get, mock_get_config):
        """Test GET request that raises RequestException."""
        mock_get_config.return_value = self.mock_config

        mock_session_get.side_effect = requests.RequestException("Connection error")

        client = HTTPClient()

        with self.assertRaises(NetworkError) as cm:
            client.get("https://example.com")

        self.assertIn("HTTP request failed for https://example.com", str(cm.exception))
        self.assertIn("Connection error", str(cm.exception))

    @patch("the_data_packet.core.config.get_config")
    @patch("requests.Session.get")
    def test_get_http_error(self, mock_session_get, mock_get_config):
        """Test GET request that returns HTTP error status."""
        mock_get_config.return_value = self.mock_config

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session_get.return_value = mock_response

        client = HTTPClient()

        with self.assertRaises(NetworkError) as cm:
            client.get("https://example.com")

        self.assertIn("HTTP request failed for https://example.com", str(cm.exception))
        self.assertIn("404 Not Found", str(cm.exception))

    @patch("the_data_packet.core.config.get_config")
    @patch.object(HTTPClient, "get")
    def test_get_soup_success(self, mock_get, mock_get_config):
        """Test successful get_soup request."""
        mock_get_config.return_value = self.mock_config

        # Mock response with HTML content
        mock_response = Mock()
        mock_response.content = b"<html><body><h1>Test</h1></body></html>"
        mock_get.return_value = mock_response

        client = HTTPClient()
        soup = client.get_soup("https://example.com")

        self.assertIsInstance(soup, BeautifulSoup)
        mock_get.assert_called_once_with("https://example.com")

        # Check that we can parse the HTML
        h1_tag = soup.find("h1")
        self.assertIsNotNone(h1_tag)
        self.assertEqual(h1_tag.text, "Test")

    @patch("the_data_packet.core.config.get_config")
    @patch.object(HTTPClient, "get")
    def test_get_soup_with_kwargs(self, mock_get, mock_get_config):
        """Test get_soup with additional keyword arguments."""
        mock_get_config.return_value = self.mock_config

        mock_response = Mock()
        mock_response.content = b"<html><body>Test</body></html>"
        mock_get.return_value = mock_response

        client = HTTPClient()
        client.get_soup("https://example.com", headers={"Custom": "Header"})

        mock_get.assert_called_once_with(
            "https://example.com", headers={"Custom": "Header"}
        )

    @patch("the_data_packet.core.config.get_config")
    @patch.object(HTTPClient, "get")
    def test_get_soup_network_error(self, mock_get, mock_get_config):
        """Test get_soup when underlying GET request fails."""
        mock_get_config.return_value = self.mock_config

        mock_get.side_effect = NetworkError("Network failure")

        client = HTTPClient()

        with self.assertRaises(NetworkError):
            client.get_soup("https://example.com")

    @patch("the_data_packet.core.config.get_config")
    def test_session_reuse(self, mock_get_config):
        """Test that the same session is reused for multiple requests."""
        mock_get_config.return_value = self.mock_config

        client = HTTPClient()

        # Sessions should be the same object
        session1 = client.session
        session2 = client.session

        self.assertIs(session1, session2)

    @patch("the_data_packet.core.config.get_config")
    def test_user_agent_in_session(self, mock_get_config):
        """Test that user agent is properly set in session."""
        mock_get_config.return_value = self.mock_config

        client = HTTPClient(user_agent="Custom Test Agent")

        self.assertEqual(client.session.headers["User-Agent"], "Custom Test Agent")


if __name__ == "__main__":
    unittest.main()
