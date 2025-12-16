"""Unified configuration system for The Data Packet."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Config:
    """Unified configuration for The Data Packet with environment variable support."""

    # API Keys
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: Optional[str] = None

    # Podcast Configuration
    show_name: str = "The Data Packet"
    episode_number: Optional[int] = None
    output_directory: Path = Path("./output")

    # Article Collection
    max_articles_per_source: int = 1
    article_sources: List[str] = field(default_factory=lambda: ["wired"])
    article_categories: List[str] = field(
        default_factory=lambda: ["security", "guide"])

    # AI Generation Settings
    claude_model: str = "claude-sonnet-4-5-20250929"
    gemini_model: str = "gemini-2.5-pro-preview-tts"
    max_tokens: int = 3000
    temperature: float = 0.7

    # Audio Settings
    voice_a: str = "Puck"
    voice_b: str = "Kore"
    audio_sample_rate: int = 24000

    # Processing Options
    generate_script: bool = True
    generate_audio: bool = True
    generate_rss: bool = True
    save_intermediate_files: bool = False
    cleanup_temp_files: bool = True

    # RSS Feed Configuration
    rss_channel_title: Optional[str] = "The Data Packet"
    rss_channel_description: Optional[str] = None
    rss_channel_link: Optional[str] = None
    rss_channel_image_url: Optional[str] = "https://the-data-packet.s3.us-west-2.amazonaws.com/the-data-packet/the_data_packet.png"
    # Contact email for podcast
    rss_channel_email: Optional[str] = "contact@securitytechhelp.com"
    max_rss_episodes: int = 500

    # Network Settings
    http_timeout: int = 30
    user_agent: str = (
        "The Data Packet/1.0 (+https://github.com/TheWinterShadow/The-Data-Packet)"
    )

    # Logging
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        self._load_from_env()
        self._validate()

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # API Keys
        self.anthropic_api_key = self.anthropic_api_key or os.getenv(
            "ANTHROPIC_API_KEY"
        )
        self.google_api_key = (
            self.google_api_key
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        # AWS
        self.aws_access_key_id = self.aws_access_key_id or os.getenv(
            "AWS_ACCESS_KEY_ID"
        )
        self.aws_secret_access_key = self.aws_secret_access_key or os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.aws_region = os.getenv("AWS_REGION", self.aws_region)
        self.s3_bucket_name = self.s3_bucket_name or os.getenv(
            "S3_BUCKET_NAME")

        # Other settings
        if env_show_name := os.getenv("SHOW_NAME"):
            self.show_name = env_show_name
        if env_log_level := os.getenv("LOG_LEVEL"):
            self.log_level = env_log_level
        if env_output_dir := os.getenv("OUTPUT_DIRECTORY"):
            self.output_directory = Path(env_output_dir)

        # RSS configuration
        if env_rss_title := os.getenv("RSS_CHANNEL_TITLE"):
            self.rss_channel_title = env_rss_title
        if env_rss_desc := os.getenv("RSS_CHANNEL_DESCRIPTION"):
            self.rss_channel_description = env_rss_desc
        if env_rss_link := os.getenv("RSS_CHANNEL_LINK"):
            self.rss_channel_link = env_rss_link
        if env_rss_image := os.getenv("RSS_CHANNEL_IMAGE_URL"):
            self.rss_channel_image_url = env_rss_image
        if env_rss_email := os.getenv("RSS_CHANNEL_EMAIL"):
            self.rss_channel_email = env_rss_email

        # Convert string env vars to proper types
        if env_max_articles := os.getenv("MAX_ARTICLES_PER_SOURCE"):
            try:
                self.max_articles_per_source = int(env_max_articles)
            except ValueError:
                pass

        if env_max_episodes := os.getenv("MAX_RSS_EPISODES"):
            try:
                self.max_rss_episodes = int(env_max_episodes)
            except ValueError:
                pass

        if env_generate_rss := os.getenv("GENERATE_RSS"):
            self.generate_rss = env_generate_rss.lower() in ("true", "1", "yes")

        if env_timeout := os.getenv("HTTP_TIMEOUT"):
            try:
                self.http_timeout = int(env_timeout)
            except ValueError:
                pass

    def _validate(self) -> None:
        """Validate configuration."""
        errors = []

        # Ensure output directory exists
        if not self.output_directory.exists():
            try:
                self.output_directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(
                    f"Cannot create output directory {self.output_directory}: {e}"
                )

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.log_level}")

        if errors:
            from .exceptions import ConfigurationError

            raise ConfigurationError(
                f"Configuration validation failed: {'; '.join(errors)}"
            )

    def validate_for_script_generation(self) -> None:
        """Validate configuration for script generation."""
        if not self.anthropic_api_key:
            from .exceptions import ConfigurationError

            raise ConfigurationError(
                "Anthropic API key is required for script generation"
            )

    def validate_for_audio_generation(self) -> None:
        """Validate configuration for audio generation."""
        if not self.google_api_key:
            from .exceptions import ConfigurationError

            raise ConfigurationError(
                "Google API key is required for audio generation")

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Path):
                result[field_name] = str(field_value)
            else:
                result[field_name] = field_value
        return result


# Global configuration instance
_config: Optional[Config] = None


def get_config(**overrides: Any) -> Config:
    """
    Get the global configuration instance.

    Args:
        **overrides: Configuration values to override

    Returns:
        Config instance
    """
    global _config
    if _config is None or overrides:
        _config = Config(**overrides)
    return _config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config
    _config = None
