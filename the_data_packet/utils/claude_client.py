import os
from typing import Dict, Optional

import requests

"""
Simple client for interacting with the Anthropic Claude API.
"""


class ClaudeClient:
    """A simple client for interacting with the Anthropic Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude client.

        Args:
            api_key: Anthropic API key. If None, will try to get from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key must be provided or set in ANTHROPIC_API_KEY environment variable")

        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    def send_message(
        self,
        message: str,
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 1000,
        system: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, str]:
        """
        Send a message to Claude and get a response.

        Args:
            message: The message to send to Claude
            model: The Claude model to use
            max_tokens: Maximum tokens in the response
            system: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Dictionary containing the API response
        """
        messages = [{"role": "user", "content": message}]

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }

        if system:
            payload["system"] = system

        response = requests.post(
            f"{self.base_url}/messages",
            headers=self.headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(
                f"API request failed: {response.status_code} - {response.text}")

        return response.json()

    def get_response_text(self, response: Dict) -> str:
        """
        Extract the text content from a Claude API response.

        Args:
            response: The response dictionary from send_message()

        Returns:
            The text content of Claude's response
        """
        if "content" in response and len(response["content"]) > 0:
            return response["content"][0]["text"]
        return ""

    def chat(
        self,
        message: str,
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 1000,
        system: Optional[str] = None,
        temperature: float = 0.7
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
        """
        response = self.send_message(
            message, model, max_tokens, system, temperature)
        return self.get_response_text(response)
