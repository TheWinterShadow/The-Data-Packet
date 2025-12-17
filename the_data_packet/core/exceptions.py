"""Custom exceptions for The Data Packet.

This module provides a hierarchy of custom exceptions for different types of errors
that can occur during podcast generation. All exceptions inherit from the base
TheDataPacketError class for easy catching.

Exception Hierarchy:
    TheDataPacketError
    ├── ConfigurationError (Missing/invalid API keys, settings)
    ├── NetworkError (HTTP requests, connectivity issues)
    ├── ScrapingError (Article extraction failures)
    ├── AIGenerationError (Claude API failures, content generation)
    ├── AudioGenerationError (Gemini TTS failures, audio processing)
    └── ValidationError (Invalid data, missing required fields)

Example:
    try:
        pipeline = PodcastPipeline()
        result = pipeline.run()
    except ConfigurationError as e:
        logger.error(f"Configuration issue: {e}")
    except AIGenerationError as e:
        logger.error(f"AI generation failed: {e}")
    except TheDataPacketError as e:
        logger.error(f"Unexpected error: {e}")
"""


class TheDataPacketError(Exception):
    """Base exception for all The Data Packet errors.

    This is the parent class for all custom exceptions in The Data Packet.
    Use this for general error handling when you want to catch any
    podcast generation related error.

    Attributes:
        message: Human-readable error description

    Example:
        try:
            pipeline.run()
        except TheDataPacketError as e:
            logger.error(f"Podcast generation failed: {e}")
    """

    pass


class ConfigurationError(TheDataPacketError):
    """Raised when there's an issue with configuration.

    This exception is raised when:
    - Required API keys are missing (ANTHROPIC_API_KEY, GOOGLE_API_KEY)
    - Invalid configuration values are provided
    - Required environment variables are not set
    - AWS credentials are missing for S3 uploads

    Example:
        if not self.anthropic_api_key:
            raise ConfigurationError("Anthropic API key is required")
    """

    pass


class NetworkError(TheDataPacketError):
    """Raised when there's a network-related error.

    This exception is raised when:
    - HTTP requests fail (timeouts, connection errors)
    - RSS feeds are unreachable
    - API services are unavailable
    - S3 upload failures due to network issues

    Example:
        try:
            response = requests.get(url, timeout=30)
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch {url}: {e}")
    """

    pass


class ScrapingError(TheDataPacketError):
    """Raised when article scraping fails.

    This exception is raised when:
    - RSS feed parsing fails
    - Article content extraction fails
    - Required article fields are missing
    - Content cleaning/processing fails

    Example:
        if not article_content:
            raise ScrapingError(f"No content found for article: {url}")
    """

    pass


class AIGenerationError(TheDataPacketError):
    """Raised when AI content generation fails.

    This exception is raised when:
    - Claude API returns errors or rate limits
    - Generated content is invalid or too short
    - AI refuses to process certain content types
    - Script generation fails after retries

    Example:
        if response.status_code != 200:
            raise AIGenerationError(f"Claude API error: {response.text}")
    """

    pass


class AudioGenerationError(TheDataPacketError):
    """Raised when audio generation fails.

    This exception is raised when:
    - Gemini TTS API returns errors
    - Audio file generation fails
    - Invalid voice configuration
    - Audio processing or saving fails

    Example:
        if not output_file.exists():
            raise AudioGenerationError("Audio file generation failed")
    """

    pass


class ValidationError(TheDataPacketError):
    """Raised when data validation fails.

    This exception is raised when:
    - Invalid article categories are provided
    - Required data fields are missing or malformed
    - Configuration values are outside acceptable ranges
    - File paths are invalid or inaccessible

    Example:
        if category not in self.supported_categories:
            raise ValidationError(f"Unsupported category: {category}")
    """

    pass
