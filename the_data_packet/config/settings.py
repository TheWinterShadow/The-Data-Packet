"""Configuration settings for The Data Packet package."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


class ConfigurationError(Exception):
    """Raised when there's an issue with configuration."""

    pass


@dataclass
class Settings:
    """Application settings with sensible defaults and environment variable support."""

    # API Keys
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    google_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )

    # HTTP Client Settings
    http_timeout: int = 30
    user_agent: str = (
        "The Data Packet/1.0 (+https://github.com/TheWinterShadow/the_data_packet)"
    )

    # Scraping Settings
    max_articles_per_category: int = 10
    supported_categories: List[str] = field(default_factory=lambda: ["security", "guide"])

    # AI Generation Settings
    claude_model: str = "claude-3-5-sonnet-20241022"
    gemini_model: str = "gemini-2.5-pro-preview-tts"
    max_tokens: int = 3000
    temperature: float = 0.7

    # Audio Settings
    audio_sample_rate: int = 24000
    audio_chunk_size: int = 8000
    default_voice_a: str = "Puck"
    default_voice_b: str = "Kore"

    # Podcast Settings
    show_name: str = "Tech Daily"
    output_directory: Path = field(default_factory=lambda: Path("./output"))

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Ensure output directory exists
        self.output_directory = Path(self.output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Validate API keys when needed
        self._validate_api_keys()

    def _validate_api_keys(self) -> None:
        """Validate that required API keys are present."""
        if not self.anthropic_api_key:
            raise ConfigurationError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable."
            )

        if not self.google_api_key:
            raise ConfigurationError(
                "Google API key is required for TTS. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
            )

    def validate_for_scraping(self) -> bool:
        """Check if configuration is valid for scraping operations."""
        return True  # Scraping doesn't require API keys

    def validate_for_ai_generation(self) -> bool:
        """Check if configuration is valid for AI operations."""
        return bool(self.anthropic_api_key)

    def validate_for_audio_generation(self) -> bool:
        """Check if configuration is valid for audio generation."""
        return bool(self.google_api_key)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset global settings instance (useful for testing)."""
    global _settings
    _settings = None
