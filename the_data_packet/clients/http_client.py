"""HTTP client for fetching web pages."""

import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client for fetching and parsing web pages."""

    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        """
        Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds
            user_agent: Custom User-Agent string
        """
        self.timeout = timeout
        self.session = requests.Session()

        if user_agent:
            self.session.headers.update({"User-Agent": user_agent})
        else:
            # Use a standard browser User-Agent
            self.session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            )

    def get_page(self, url: str) -> BeautifulSoup:
        """
        Fetch a web page and return a BeautifulSoup object.

        Args:
            url: The URL to fetch

        Returns:
            BeautifulSoup object of the parsed HTML

        Raises:
            RuntimeError: If the request fails
        """
        logger.info(f"Fetching URL: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            logger.info(f"Successfully fetched {url} (status: {response.status_code})")
            return BeautifulSoup(response.text, "html.parser")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    def get_raw_content(self, url: str) -> str:
        """
        Fetch raw HTML content from a URL.

        Args:
            url: The URL to fetch

        Returns:
            Raw HTML content as string
        """
        logger.info(f"Fetching raw content from: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching raw content from {url}: {e}")
            raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
