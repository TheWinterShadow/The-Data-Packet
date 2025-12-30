"""Audio generation using Google Cloud Text-to-Speech Long Audio Synthesis."""

import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from google.cloud import storage, texttospeech  # type: ignore[attr-defined]
from google.oauth2 import service_account

from the_data_packet.core.config import get_config
from the_data_packet.core.exceptions import AudioGenerationError, ConfigurationError
from the_data_packet.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AudioResult:
    """Result of audio generation."""

    output_file: Path
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    generation_time_seconds: Optional[float] = None


class AudioGenerator:
    """Generates podcast audio from scripts using Google Cloud Text-to-Speech Long Audio Synthesis."""

    # Available Studio Multi-speaker voices for podcast content
    AVAILABLE_VOICES = {
        "male": [
            "en-US-Studio-MultiSpeaker-R",  # Alex (male narrator)
            "en-US-Studio-MultiSpeaker-T",  # Additional male voice
            "en-US-Studio-MultiSpeaker-V",  # Another male option
        ],
        "female": [
            "en-US-Studio-MultiSpeaker-S",  # Sam (female narrator)
            "en-US-Studio-MultiSpeaker-U",  # Additional female voice
            "en-US-Studio-MultiSpeaker-W",  # Another female option
        ],
    }

    # Audio encoding settings for long audio synthesis
    AUDIO_CONFIG = {
        "audio_encoding": texttospeech.AudioEncoding.MP3,
        "sample_rate_hertz": 44100,
        # Optimized for voice
        "effects_profile_id": ["telephony-class-application"],
    }

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        voice_a: Optional[str] = None,
        voice_b: Optional[str] = None,
        gcs_bucket_name: Optional[str] = None,
    ):
        """
        Initialize the audio generator.

        Args:
            credentials_path: Path to Google Cloud service account JSON credentials
            voice_a: Voice name for first speaker (Alex)
            voice_b: Voice name for second speaker (Sam)
            gcs_bucket_name: Google Cloud Storage bucket for audio output
        """
        config = get_config()

        self.credentials_path = credentials_path or getattr(
            config, "google_credentials_path", None
        )
        self.voice_a = voice_a or getattr(
            config, "voice_a", "en-US-Studio-MultiSpeaker-R"
        )
        self.voice_b = voice_b or getattr(
            config, "voice_b", "en-US-Studio-MultiSpeaker-S"
        )
        self.gcs_bucket_name = gcs_bucket_name or getattr(
            config, "gcs_bucket_name", None
        )
        self.config = config

        if not self.gcs_bucket_name:
            raise ConfigurationError(
                "Google Cloud Storage bucket is required for long audio synthesis. "
                "Set gcs_bucket_name in config or provide gcs_bucket_name parameter."
            )

        # Initialize Google Cloud clients
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.tts_client = texttospeech.TextToSpeechLongAudioSynthesizeClient(
                    credentials=credentials
                )
                self.storage_client = storage.Client(credentials=credentials)
            else:
                # Use default application credentials
                self.tts_client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
                self.storage_client = storage.Client()

            logger.info("Initialized Google Cloud Text-to-Speech Long Audio client")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Google Cloud clients: {e}")

        # Validate GCS bucket access
        self._validate_gcs_bucket()

        logger.info(
            f"Initialized Google Cloud TTS generator with voices: {self.voice_a}, {self.voice_b} and bucket: {self.gcs_bucket_name}"  # noqa: E501
        )

    def _validate_gcs_bucket(self) -> None:
        """Validate that the GCS bucket is accessible."""
        try:
            bucket = self.storage_client.bucket(self.gcs_bucket_name)
            # Test bucket access by attempting to list objects (just checking first one)
            list(bucket.list_blobs(max_results=1))
            logger.info(
                f"Successfully validated access to GCS bucket: {self.gcs_bucket_name}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Cannot access GCS bucket '{self.gcs_bucket_name}': {e}. "
                "Ensure the bucket exists and you have proper permissions."
            )

    def generate_audio(
        self, script: str, output_file: Optional[Path] = None
    ) -> AudioResult:
        """
        Generate audio from a podcast script using Google Cloud Text-to-Speech Long Audio Synthesis.

        Args:
            script: Podcast script text
            output_file: Output file path (defaults to config output directory)

        Returns:
            AudioResult with generation details

        Raises:
            AudioGenerationError: If audio generation fails
        """
        if not script or len(script.strip()) < 100:
            raise AudioGenerationError("Script too short or empty")

        if output_file is None:
            # Use .mp3 extension for Spotify compatibility
            output_file = self.config.output_directory / "episode.mp3"

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating audio to {output_file}")
        start_time = datetime.now()

        try:
            # Parse and prepare script as single SSML for long audio synthesis
            ssml_content = self._parse_script_to_ssml(script)

            if not ssml_content:
                raise AudioGenerationError("No valid content found in script")

            logger.info(f"Generated SSML content ({len(ssml_content)} characters)")

            # Generate audio using Google Cloud Long Audio Synthesis
            gcs_uri = self._generate_with_long_audio_synthesis(ssml_content)

            # Download the generated audio from GCS
            self._download_audio_from_gcs(gcs_uri, output_file)

            # Calculate metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            file_size = output_file.stat().st_size if output_file.exists() else None

            logger.info(f"Audio generation completed in {generation_time:.1f} seconds")

            return AudioResult(
                output_file=output_file,
                generation_time_seconds=generation_time,
                file_size_bytes=file_size,
            )

        except Exception as e:
            if isinstance(e, AudioGenerationError):
                raise
            raise AudioGenerationError(f"Audio generation failed: {e}")

    def _parse_script_to_ssml(self, script: str) -> str:
        """Parse script and convert to SSML with voice switching for multi-speaker synthesis."""
        lines = script.split("\n")
        ssml_parts = ["<speak>"]

        for line in lines:
            line = line.strip()

            # Skip empty lines, headers, and formatting
            if not line or line.startswith("#") or line.startswith("**"):
                continue

            # Handle dialogue lines with voice switching
            if line.startswith("Alex:"):
                content = line[5:].strip()
                ssml_parts.append(f'<voice name="{self.voice_a}">{content}</voice>')
                # Pause between speakers
                ssml_parts.append('<break time="0.5s"/>')
            elif line.startswith("Sam:"):
                content = line[4:].strip()
                ssml_parts.append(f'<voice name="{self.voice_b}">{content}</voice>')
                # Pause between speakers
                ssml_parts.append('<break time="0.5s"/>')
            else:
                # Non-dialogue text - assign to Alex (default narrator)
                if line:
                    ssml_parts.append(f'<voice name="{self.voice_a}">{line}</voice>')
                    # Short pause for continuity
                    ssml_parts.append('<break time="0.3s"/>')

        ssml_parts.append("</speak>")

        # Join and clean up extra breaks
        ssml_content = "".join(ssml_parts)
        # Remove any trailing breaks before closing speak tag
        ssml_content = ssml_content.replace('<break time="0.5s"/></speak>', "</speak>")
        ssml_content = ssml_content.replace('<break time="0.3s"/></speak>', "</speak>")

        return ssml_content

    def _generate_with_long_audio_synthesis(self, ssml_content: str) -> str:
        """Generate audio using Google Cloud Long Audio Synthesis and return GCS URI."""
        try:
            # Create the synthesis input
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_content)

            # Configure audio output settings
            audio_config = texttospeech.AudioConfig(
                audio_encoding=self.AUDIO_CONFIG["audio_encoding"],
                sample_rate_hertz=self.AUDIO_CONFIG["sample_rate_hertz"],
                effects_profile_id=self.AUDIO_CONFIG["effects_profile_id"],
            )

            # Generate unique output file name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gcs_uri = f"gs://{self.gcs_bucket_name}/audio/episode_{timestamp}.mp3"

            # Create the Long Audio Synthesis request
            request = texttospeech.SynthesizeLongAudioRequest(
                input=synthesis_input,
                audio_config=audio_config,
                output_gcs_uri=gcs_uri,
            )

            logger.info(f"Starting long audio synthesis operation to {gcs_uri}")

            # Start the Long Running Operation (LRO)
            operation_future = self.tts_client.synthesize_long_audio(request=request)

            logger.info(
                f"Long audio synthesis started. Operation name: {operation_future.operation.name}"
            )

            # Wait for the operation to complete with timeout and progress logging
            timeout_seconds = 1800  # 30 minutes timeout for very long audio
            poll_interval = 30  # Check every 30 seconds
            elapsed = 0

            while not operation_future.done() and elapsed < timeout_seconds:
                logger.info(
                    f"Waiting for synthesis to complete... ({elapsed}s elapsed)"
                )
                time.sleep(poll_interval)
                elapsed += poll_interval

            if not operation_future.done():
                raise AudioGenerationError(
                    f"Audio synthesis timed out after {timeout_seconds} seconds"
                )

            # Get the result
            operation_future.result()
            logger.info("Long audio synthesis completed successfully")

            return gcs_uri

        except Exception as e:
            logger.error(f"Long audio synthesis failed: {e}")
            raise AudioGenerationError(
                f"Failed to generate audio with Google Cloud TTS: {e}"
            )

    def _download_audio_from_gcs(self, gcs_uri: str, output_file: Path) -> None:
        """Download the generated audio file from Google Cloud Storage."""
        try:
            # Parse the GCS URI to get bucket and blob name
            # Format: gs://bucket-name/path/to/file.mp3
            if not gcs_uri.startswith("gs://"):
                raise AudioGenerationError(f"Invalid GCS URI format: {gcs_uri}")

            # Remove 'gs://' prefix and split bucket/path
            path_parts = gcs_uri[5:].split("/", 1)
            if len(path_parts) != 2:
                raise AudioGenerationError(f"Invalid GCS URI format: {gcs_uri}")

            bucket_name, blob_name = path_parts

            logger.info(f"Downloading audio from GCS: {gcs_uri}")

            # Get the bucket and blob
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Wait for file to be available (sometimes there's a slight delay)
            max_retries = 10
            retry_delay = 5  # seconds

            for attempt in range(max_retries):
                try:
                    if blob.exists():
                        break
                    else:
                        logger.info(
                            f"Audio file not yet available, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})"  # noqa: E501
                        )
                        time.sleep(retry_delay)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise AudioGenerationError(
                            f"Audio file not found in GCS after {max_retries} attempts: {e}"
                        )
                    logger.warning(
                        f"Error checking blob existence (attempt {attempt + 1}): {e}"
                    )
                    time.sleep(retry_delay)

            # Download the file
            blob.download_to_filename(str(output_file))
            logger.info(f"Successfully downloaded audio to {output_file}")

            # Optionally clean up the GCS file
            if getattr(self.config, "cleanup_temp_files", True):
                try:
                    blob.delete()
                    logger.info(f"Cleaned up temporary GCS file: {gcs_uri}")
                except Exception as e:
                    logger.warning(f"Could not clean up GCS file {gcs_uri}: {e}")

        except Exception as e:
            raise AudioGenerationError(
                f"Failed to download audio from GCS {gcs_uri}: {e}"
            )

    def get_available_voices(self) -> Dict[str, List[str]]:
        """Get available Studio Multi-speaker voices for Google Cloud TTS."""
        try:
            # For Google Cloud, we return the predefined Studio Multi-speaker voices
            # These are the voices specifically designed for multi-speaker content
            return self.AVAILABLE_VOICES.copy()

        except Exception as e:
            logger.warning(f"Could not retrieve available voices: {e}")
            # Return available voices as fallback
            return self.AVAILABLE_VOICES

    def test_authentication(self) -> bool:
        """Test Google Cloud TTS authentication and basic functionality."""
        try:
            # Test TTS client by listing available voices
            request = texttospeech.ListVoicesRequest(language_code="en-US")

            # Use the regular TTS client for testing (not long audio client)
            test_client = texttospeech.TextToSpeechClient(
                credentials=(
                    self.tts_client._credentials
                    if hasattr(self.tts_client, "_credentials")
                    else None
                )
            )

            voices_response = test_client.list_voices(request=request)

            if voices_response.voices:
                logger.info(
                    f"Authentication successful! Retrieved {len(voices_response.voices)} voices."
                )

                # Also test GCS bucket access
                bucket = self.storage_client.bucket(self.gcs_bucket_name)
                bucket.exists()  # This will raise an exception if no access

                logger.info(f"GCS bucket access confirmed: {self.gcs_bucket_name}")
                return True
            else:
                logger.warning("Authentication successful but no voices found")
                return False

        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False
