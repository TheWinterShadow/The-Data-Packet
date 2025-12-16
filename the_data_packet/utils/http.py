"""HTTP client utility."""

from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from the_data_packet.core.exceptions import NetworkError
from the_data_packet.core.logging import get_logger

logger = get_logger(__name__)


class HTTPClient:
    """Simple HTTP client with error handling and configuration."""

    def __init__(self, timeout: Optional[int] = None, user_agent: Optional[str] = None):
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout (defaults to config)
            user_agent: User agent string (defaults to config)
        """
        from ..core.config import get_config

        config = get_config()

        self.timeout = timeout or config.http_timeout
        self.user_agent = user_agent or config.user_agent

        # Create session
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """
        Make a GET request.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments passed to requests.get

        Returns:
            Response object

        Raises:
            NetworkError: If request fails
        """
        kwargs.setdefault("timeout", self.timeout)

        try:
            logger.debug(f"GET {url}")
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response

        except requests.RequestException as e:
            raise NetworkError(f"HTTP request failed for {url}: {e}")

    def get_soup(self, url: str, **kwargs: Any) -> BeautifulSoup:
        """
        Get a URL and return parsed HTML.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments passed to get()

        Returns:
            BeautifulSoup object

        Raises:
            NetworkError: If request fails
        """
        response = self.get(url, **kwargs)
        return BeautifulSoup(response.content, "html.parser")
