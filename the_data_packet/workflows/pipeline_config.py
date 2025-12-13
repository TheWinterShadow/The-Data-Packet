"""Configuration for the podcast generation pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from the_data_packet.config import get_settings


@dataclass
class PipelineConfig:
    """Configuration for the complete podcast generation pipeline."""

    # Episode Information
    episode_date: str = field(
        default_factory=lambda: datetime.now().strftime("%A, %B %d, %Y")
    )
    show_name: Optional[str] = None
    episode_number: Optional[int] = None

    # Source Configuration
    categories: List[str] = field(default_factory=lambda: ["security", "guide"])
    max_articles_per_category: int = 1

    # Processing Configuration
    generate_script: bool = True
    generate_audio: bool = True

    # Output Configuration
    output_directory: Optional[Path] = None
    script_filename: str = "episode_script.txt"
    audio_filename: str = "episode.wav"

    # AI Configuration
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    voice_a: Optional[str] = None
    voice_b: Optional[str] = None

    # Advanced Options
    save_intermediate_files: bool = False
    cleanup_temp_files: bool = True
    validate_results: bool = True

    def __post_init__(self):
        """Initialize configuration with defaults from settings."""
        settings = get_settings()

        # Set defaults from settings if not provided
        if self.show_name is None:
            self.show_name = settings.show_name

        if self.output_directory is None:
            self.output_directory = settings.output_directory

        if self.anthropic_api_key is None:
            self.anthropic_api_key = settings.anthropic_api_key

        if self.google_api_key is None:
            self.google_api_key = settings.google_api_key

        if self.voice_a is None:
            self.voice_a = settings.default_voice_a

        if self.voice_b is None:
            self.voice_b = settings.default_voice_b

        # Ensure output directory exists
        if self.output_directory:
            Path(self.output_directory).mkdir(parents=True, exist_ok=True)

    def get_script_path(self) -> Path:
        """Get full path for the script output file."""
        return Path(self.output_directory) / self.script_filename

    def get_audio_path(self) -> Path:
        """Get full path for the audio output file."""
        return Path(self.output_directory) / self.audio_filename

    def validate(self) -> List[str]:
        """
        Validate the configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if self.generate_script and not self.anthropic_api_key:
            errors.append("Anthropic API key required for script generation")

        if self.generate_audio and not self.google_api_key:
            errors.append("Google API key required for audio generation")

        if not self.categories:
            errors.append("At least one category must be specified")

        if self.max_articles_per_category < 1:
            errors.append("max_articles_per_category must be at least 1")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "episode_date": self.episode_date,
            "show_name": self.show_name,
            "episode_number": self.episode_number,
            "categories": self.categories,
            "max_articles_per_category": self.max_articles_per_category,
            "generate_script": self.generate_script,
            "generate_audio": self.generate_audio,
            "output_directory": (
                str(self.output_directory) if self.output_directory else None
            ),
            "script_filename": self.script_filename,
            "audio_filename": self.audio_filename,
            "voice_a": self.voice_a,
            "voice_b": self.voice_b,
            "save_intermediate_files": self.save_intermediate_files,
            "cleanup_temp_files": self.cleanup_temp_files,
            "validate_results": self.validate_results,
        }
