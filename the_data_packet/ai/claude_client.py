"""Improved Claude API client with better error handling and configuration."""

from typing import Dict, Optional, Any

import requests

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:
    # Fallback if tenacity is not available
    def retry(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    stop_after_attempt = wait_exponential = lambda *args, **kwargs: None

from the_data_packet.config import get_settings
from the_data_packet.core.exceptions import AIGenerationError, NetworkError
from the_data_packet.core.logging_config import get_logger

logger = get_logger(__name__)


class ClaudeClient:
    """
    Enhanced client for interacting with the Anthropic Claude API.

    Features:
    - Automatic retry logic with exponential backoff
    - Better error handling and logging
    - Configuration integration
    - Rate limiting awareness
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Claude client.

        Args:
            api_key: Anthropic API key. If None, will get from settings.
            model: Default model to use. If None, will get from settings.
        """
        settings = get_settings()

        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise AIGenerationError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable."
            )

        self.default_model = model or settings.claude_model
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        logger.info(f"Initialized Claude client with model: {self.default_model}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def send_message(
        self,
        message: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[Any, Any]:
        """
        Send a message to Claude and get a response with retry logic.

        Args:
            message: The message to send to Claude
            model: The Claude model to use (defaults to configured model)
            max_tokens: Maximum tokens in the response
            system: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Dictionary containing the API response

        Raises:
            AIGenerationError: If the API request fails
            NetworkError: If there's a network-related issue
        """
        settings = get_settings()

        # Use provided values or defaults from settings
        model = model or self.default_model
        max_tokens = max_tokens or settings.max_tokens
        temperature = temperature or settings.temperature

        messages = [{"role": "user", "content": message}]

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }

        if system:
            payload["system"] = system

        logger.debug(f"Sending message to Claude API: {len(message)} characters")

        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=60,
            )

            if response.status_code == 429:
                logger.warning("Rate limit hit, retrying...")
                raise NetworkError("Rate limit exceeded")

            if response.status_code != 200:
                error_msg = (
                    f"API request failed: {response.status_code} - {response.text}"
                )
                logger.error(error_msg)
                raise AIGenerationError(error_msg)

            logger.debug("Successfully received response from Claude API")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error communicating with Claude API: {e}")
            raise NetworkError(f"Network error: {e}") from e

    def get_response_text(self, response: Dict) -> str:
        """
        Extract the text content from a Claude API response.

        Args:
            response: The response dictionary from send_message()

        Returns:
            The text content of Claude's response
        """
        try:
            if "content" in response and len(response["content"]) > 0:
                return response["content"][0]["text"]
            return ""
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting text from Claude response: {e}")
            raise AIGenerationError("Invalid response format from Claude API") from e

    def chat(
        self,
        message: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Convenience method that sends a message and returns just the text response.

        Args:
            message: The message to send to Claude
            model: The Claude model to use
            max_tokens: Maximum tokens in the response
            system: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Claude's text response

        Raises:
            AIGenerationError: If the generation fails
        """
        response = self.send_message(message, model, max_tokens, system, temperature)
        return self.get_response_text(response)

    def validate_connection(self) -> bool:
        """
        Test the connection to the Claude API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_response = self.chat(
                message="Hello, please respond with just 'OK'", max_tokens=10
            )
            return "OK" in test_response
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False
