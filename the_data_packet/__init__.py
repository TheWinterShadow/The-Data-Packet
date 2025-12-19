"""
The Data Packet - Automated podcast generation from news articles.

This package provides end-to-end tools for:
- Collecting articles from multiple news sources
- Generating podcast scripts using Claude AI
- Creating audio content using ElevenLabs TTS
- Complete workflow orchestration

Main Components:
- PodcastPipeline: Complete workflow orchestration
- ArticleSource: Extensible article collection
- ScriptGenerator: AI-powered script generation
- AudioGenerator: Multi-speaker audio generation
- Config: Unified configuration management
- SimplePodcastGenerator: Simplified one-line interface

Quick Start:
    >>> from the_data_packet import PodcastPipeline
    >>> pipeline = PodcastPipeline()
    >>> result = pipeline.run()

Simplified Interface:
    >>> from the_data_packet import SimplePodcastGenerator
    >>> generator = SimplePodcastGenerator(s3_bucket="my-bucket")
    >>> result = generator.generate_podcast(show_name="My Show")

Individual Components:
    >>> from the_data_packet.sources import WiredSource, TechCrunchSource
    >>> from the_data_packet.generation import ScriptGenerator, AudioGenerator
    >>> from the_data_packet.utils import S3Storage
"""

from the_data_packet.__about__ import __version__

# Core components
from the_data_packet.core import (
    AIGenerationError,
    AudioGenerationError,
    Config,
    ConfigurationError,
    NetworkError,
    ScrapingError,
    TheDataPacketError,
    ValidationError,
    get_config,
    get_logger,
    setup_logging,
)

# Generation modules
from the_data_packet.generation import (
    AudioGenerator,
    ScriptGenerator,
)

# Article sources
from the_data_packet.sources import (
    Article,
    ArticleSource,
    TechCrunchSource,
    WiredSource,
)

# Storage modules
from the_data_packet.utils import (
    S3Storage,
    S3UploadResult,
)

# Main workflows
from the_data_packet.workflows import (
    PodcastPipeline,
    PodcastResult,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "Config",
    "get_config",
    "setup_logging",
    "get_logger",
    # Exceptions
    "TheDataPacketError",
    "ConfigurationError",
    "ScrapingError",
    "AIGenerationError",
    "AudioGenerationError",
    "ValidationError",
    "NetworkError",
    # Sources
    "ArticleSource",
    "Article",
    "TechCrunchSource",
    "WiredSource",
    # Generation
    "ScriptGenerator",
    "AudioGenerator",
    # Storage
    "S3Storage",
    "S3UploadResult",
    # Workflows
    "PodcastPipeline",
    "PodcastResult",
    # Simplified interface
    "SimplePodcastGenerator",
    "SimplePodcastResult",
]
