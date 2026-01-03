"""Unified configuration system for The Data Packet.

This module provides centralized configuration management with support for:
- Environment variable loading
- Type-safe configuration with validation
- Default values for all settings
- Global configuration singleton pattern
- Override capabilities for testing

The configuration system follows these priorities (highest to lowest):
1. Direct parameter overrides
2. Environment variables
3. Default values

Configuration Categories:
    API Keys:
        - Anthropic API key for Claude script generation
        - ElevenLabs API key for TTS audio generation
        - AWS credentials for S3 storage

    Podcast Settings:
        - Show metadata (name, episode numbers)
        - Audio preferences (voices, sample rate)
        - RSS feed configuration

    Processing Options:
        - Which generation steps to run
        - Article collection preferences
        - Output and cleanup settings

    Network Settings:
        - HTTP timeouts and user agents
        - Retry configurations
        - Rate limiting settings

Usage:
    # Get default configuration (loads from environment)
    config = get_config()

    # Override specific values
    config = get_config(
        show_name="My Custom Podcast",
        max_articles_per_source=3
    )

    # Access configuration values
    if config.anthropic_api_key:
        generator = ScriptGenerator(config.anthropic_api_key)

Environment Variables:
    Required for script generation:
        ANTHROPIC_API_KEY - Claude API key

    Required for audio generation:
        GCS_BUCKET_NAME - Google Cloud Storage bucket for long audio synthesis
        GOOGLE_APPLICATION_CREDENTIALS - Path to service account JSON (optional if using default credentials)

    Legacy (deprecated):
        ELEVENLABS_API_KEY - ElevenLabs API key (replaced by Google Cloud TTS)

    Optional for S3 uploads:
        S3_BUCKET_NAME - S3 bucket for hosting
        AWS_ACCESS_KEY_ID - AWS access key
        AWS_SECRET_ACCESS_KEY - AWS secret key
        AWS_REGION - AWS region (default: us-east-1)

    Optional for Grafana Loki log aggregation:
        GRAFANA_LOKI_URL - Loki endpoint URL
        GRAFANA_LOKI_USERNAME - Loki authentication username
        GRAFANA_LOKI_PASSWORD - Loki authentication password/API key

    Optional customizations:
        SHOW_NAME - Podcast name override
        LOG_LEVEL - Logging level (DEBUG/INFO/WARNING/ERROR)
        MAX_ARTICLES - Max articles per source

    Logging configuration:
        LOG_DIRECTORY - Directory for JSONL log files (default: output/logs)
        ENABLE_JSONL_LOGGING - Enable JSONL file logging (true/false, default: true)
        ENABLE_S3_LOG_UPLOAD - Enable S3 upload of logs (true/false, default: true)
        LOG_UPLOAD_INTERVAL - Upload interval in seconds (default: 3600)
        REMOVE_LOGS_AFTER_UPLOAD - Remove local logs after S3 upload (true/false, default: false)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from the_data_packet.core.exceptions import ConfigurationError


@dataclass
class Config:
    """Unified configuration for The Data Packet with environment variable support.

    This class provides type-safe configuration management with automatic
    environment variable loading and validation. All fields have sensible
    defaults and can be overridden via environment variables or direct
    parameter passing.

    Attributes:
        API Keys:
            anthropic_api_key: Anthropic API key for Claude script generation.
                              Required for script generation. Loaded from ANTHROPIC_API_KEY.
            elevenlabs_api_key: [DEPRECATED] ElevenLabs API key for legacy TTS.
                               Replaced by Google Cloud TTS. Loaded from ELEVENLABS_API_KEY.
            mongodb_username: MongoDB username for episode tracking and article deduplication.
                             Optional. Loaded from MONGODB_USERNAME.
            mongodb_password: MongoDB password for episode tracking and article deduplication.
                             Optional. Loaded from MONGODB_PASSWORD.

        Google Cloud Configuration:
            google_credentials_path: Path to Google Cloud service account JSON file.
                                   Optional if using default application credentials.
                                   Loaded from GOOGLE_APPLICATION_CREDENTIALS.
            gcs_bucket_name: Google Cloud Storage bucket for long audio synthesis output.
                           Required for audio generation. Loaded from GCS_BUCKET_NAME.

        AWS Configuration:
            aws_access_key_id: AWS access key for S3 uploads. Loaded from AWS_ACCESS_KEY_ID.
            aws_secret_access_key: AWS secret key for S3 uploads. Loaded from AWS_SECRET_ACCESS_KEY.
            aws_region: AWS region for S3 operations. Default: us-east-1.
            s3_bucket_name: S3 bucket name for hosting files. Loaded from S3_BUCKET_NAME.
        Grafana Loki Configuration:
            grafana_loki_url: Loki endpoint URL for log aggregation. Loaded from GRAFANA_LOKI_URL.
            grafana_loki_username: Username for Loki authentication. Loaded from GRAFANA_LOKI_USERNAME.
            grafana_loki_password: Password/API key for Loki authentication. Loaded from GRAFANA_LOKI_PASSWORD.
        Podcast Configuration:
            show_name: Podcast show name. Used in RSS feeds and file names.
            episode_number: Episode number for RSS feeds. Auto-generated if None.
            output_directory: Local directory for generated files.

        Article Collection:
            max_articles_per_source: Maximum articles to collect per source.
            article_sources: List of news sources to use (wired, techcrunch).
            article_categories: List of categories to fetch from each source.
            source_category_mapping: Maps each source to its supported categories.

        AI Generation Settings:
            claude_model: Claude model name for script generation.
            tts_model: Text-to-speech service type (now "google_cloud_tts").
            max_tokens: Maximum tokens for Claude API calls.
            temperature: AI generation temperature (0.0-1.0, lower = more consistent).

        Audio Settings (Google Cloud Studio Multi-speaker voices):
            voice_a: First speaker voice name (Alex - male narrator).
            voice_b: Second speaker voice name (Sam - female narrator).
            audio_sample_rate: Audio sample rate in Hz.

        Processing Options:
            generate_script: Whether to generate podcast scripts.
            generate_audio: Whether to generate audio files.
            generate_rss: Whether to generate RSS feeds.
            save_intermediate_files: Whether to keep intermediate processing files.
            cleanup_temp_files: Whether to clean up temporary files after processing.

        RSS Feed Configuration:
            rss_channel_title: RSS channel title.
            rss_channel_description: RSS channel description.
            rss_channel_link: RSS channel website link.
            rss_channel_image_url: RSS channel artwork URL.
            rss_channel_email: Contact email for podcast.
            max_rss_episodes: Maximum episodes to keep in RSS feed.

        Network Settings:
            http_timeout: HTTP request timeout in seconds.
            user_agent: User agent string for HTTP requests.
            log_level: Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL).

    Example:
        # Default configuration with environment variables
        config = Config()

        # Custom configuration
        config = Config(
            show_name="Tech News Daily",
            max_articles_per_source=3,
            voice_a="charon",
            voice_b="aoede"
        )

        # Validate before use
        config.validate_for_script_generation()
        config.validate_for_audio_generation()
    """

    # API Keys
    anthropic_api_key: Optional[str] = None
    # Deprecated - use Google Cloud TTS
    elevenlabs_api_key: Optional[str] = None
    mongodb_username: Optional[str] = None
    mongodb_password: Optional[str] = None

    # Google Cloud Configuration
    # Path to service account JSON
    google_credentials_path: Optional[str] = None
    # GCS bucket for long audio synthesis
    gcs_bucket_name: Optional[str] = None

    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: Optional[str] = None

    # Grafana Loki Configuration
    grafana_loki_url: Optional[str] = None
    grafana_loki_username: Optional[str] = None
    grafana_loki_password: Optional[str] = None

    # Podcast Configuration
    show_name: str = "The Data Packet"
    episode_number: Optional[int] = None
    output_directory: Path = Path("./output")

    # Article Collection
    max_articles_per_source: int = 1
    article_sources: List[str] = field(default_factory=lambda: ["wired", "techcrunch"])
    article_categories: List[str] = field(default_factory=lambda: ["security", "ai"])
    source_category_mapping: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "wired": ["security", "science", "ai"],
            "techcrunch": ["ai", "security"],
        }
    )

    # AI Generation Settings
    claude_model: str = "claude-sonnet-4-5-20250929"
    tts_model: str = "google_cloud_tts"  # Updated to use Google Cloud TTS
    max_tokens: int = 3000
    temperature: float = 0.7

    # Audio Settings (Google Cloud Studio Multi-speaker voices)
    male_voice: str = "en-US-Studio-Q"  # Alex (male narrator)
    female_voice: str = "en-US-Studio-O"  # Sam (female narrator)
    audio_sample_rate: int = 44100

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
    rss_channel_image_url: Optional[str] = (
        "https://the-data-packet.s3.us-west-2.amazonaws.com/the-data-packet/the_data_packet.png"
    )
    # Contact email for podcast
    rss_channel_email: Optional[str] = "contact@thewintershadow.com"
    max_rss_episodes: int = 500

    # Network Settings
    http_timeout: int = 30
    user_agent: str = (
        "The Data Packet/1.0 (+https://github.com/TheWinterShadow/The-Data-Packet)"
    )

    # Logging
    log_level: str = "INFO"
    log_dir: str = "output/logs"
    enable_jsonl_logging: bool = True
    enable_s3_log_upload: bool = True
    log_upload_interval: int = 3600  # seconds
    remove_logs_after_upload: bool = False

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
        self.elevenlabs_api_key = self.elevenlabs_api_key or os.getenv(
            "ELEVENLABS_API_KEY"
        )

        # Google Cloud
        self.google_credentials_path = self.google_credentials_path or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self.gcs_bucket_name = self.gcs_bucket_name or os.getenv("GCS_BUCKET_NAME")
        self.mongodb_username = self.mongodb_username or os.getenv("MONGODB_USERNAME")
        self.mongodb_password = self.mongodb_password or os.getenv("MONGODB_PASSWORD")

        # AWS
        self.aws_access_key_id = self.aws_access_key_id or os.getenv(
            "AWS_ACCESS_KEY_ID"
        )
        self.aws_secret_access_key = self.aws_secret_access_key or os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.aws_region = os.getenv("AWS_REGION", self.aws_region)
        self.s3_bucket_name = self.s3_bucket_name or os.getenv("S3_BUCKET_NAME")

        # Grafana Loki
        self.grafana_loki_url = self.grafana_loki_url or os.getenv("GRAFANA_LOKI_URL")
        self.grafana_loki_username = self.grafana_loki_username or os.getenv(
            "GRAFANA_LOKI_USERNAME"
        )
        self.grafana_loki_password = self.grafana_loki_password or os.getenv(
            "GRAFANA_LOKI_PASSWORD"
        )

        # Other settings
        if env_show_name := os.getenv("SHOW_NAME"):
            self.show_name = env_show_name
        if env_log_level := os.getenv("LOG_LEVEL"):
            self.log_level = env_log_level
        if env_log_dir := os.getenv("LOG_DIRECTORY"):
            self.log_dir = env_log_dir
        if env_enable_jsonl := os.getenv("ENABLE_JSONL_LOGGING"):
            self.enable_jsonl_logging = env_enable_jsonl.lower() in (
                "true",
                "1",
                "yes",
                "on",
            )
        if env_enable_s3_upload := os.getenv("ENABLE_S3_LOG_UPLOAD"):
            self.enable_s3_log_upload = env_enable_s3_upload.lower() in (
                "true",
                "1",
                "yes",
                "on",
            )
        if env_upload_interval := os.getenv("LOG_UPLOAD_INTERVAL"):
            try:
                self.log_upload_interval = int(env_upload_interval)
            except ValueError:
                pass
        if env_remove_logs := os.getenv("REMOVE_LOGS_AFTER_UPLOAD"):
            self.remove_logs_after_upload = env_remove_logs.lower() in (
                "true",
                "1",
                "yes",
                "on",
            )
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

        # Validate source-category compatibility
        for source in self.article_sources:
            if source not in self.source_category_mapping:
                errors.append(f"Unknown source: {source}")
            else:
                for category in self.article_categories:
                    if category not in self.source_category_mapping[source]:
                        errors.append(
                            f"Category '{category}' not supported by source '{source}'. "
                            f"Supported categories for {source}: {self.source_category_mapping[source]}"
                        )

        if errors:
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
        if not self.gcs_bucket_name:
            from .exceptions import ConfigurationError

            raise ConfigurationError(
                "Google Cloud Storage bucket is required for audio generation. "
                "Set gcs_bucket_name in config or GCS_BUCKET_NAME environment variable."
            )

    def get_sources_for_category(self, category: str) -> List[str]:
        """Get list of sources that support a given category.

        Args:
            category: Category name to check

        Returns:
            List of source names that support the category
        """
        return [
            source
            for source, categories in self.source_category_mapping.items()
            if category in categories and source in self.article_sources
        ]

    def get_categories_for_source(self, source: str) -> List[str]:
        """Get list of categories supported by a given source.

        Args:
            source: Source name to check

        Returns:
            List of category names supported by the source
        """
        if source not in self.source_category_mapping:
            return []
        return [
            category
            for category in self.source_category_mapping[source]
            if category in self.article_categories
        ]

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
