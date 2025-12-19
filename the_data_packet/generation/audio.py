"""Audio generation using ElevenLabs Text-to-Speech."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

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
    """Generates podcast audio from scripts using ElevenLabs Text-to-Speech."""

    # Available voice models and their descriptions
    AVAILABLE_MODELS = {
        "eleven_turbo_v2_5": "Ultra-fast, high-quality voices (recommended)",
        "eleven_multilingual_v2": "High-quality multilingual voices",
        "eleven_flash_v2_5": "Fast generation with good quality",
    }

    # Popular voice IDs for podcast content (Creator tier)
    DEFAULT_VOICES = {
        "male": [
            "JBFqnCBsd6RMkjVDRZzb",  # George (narrator)
            "N2lVS1w4EtoT3dr4eOWO",  # Callum (conversational)
            "5Q0t7uMcjvnagumLfvZi",  # Charlie (young adult male)
            "onwK4e9ZLuTAKqWW03F9",  # Daniel (middle-aged)
        ],
        "female": [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel (narrator)
            "AZnzlk1XvdvUeBnXmlld",  # Domi (young woman)
            "EXAVITQu4vr4xnSDxMaL",  # Bella (reading)
            "MF3mGyEYCl7XYWbV9V6O",  # Elli (emotional range)
        ],
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: Optional[str] = None,
        voice_a: Optional[str] = None,
        voice_b: Optional[str] = None,
    ):
        """
        Initialize the audio generator.

        Args:
            api_key: ElevenLabs API key
            model_id: ElevenLabs model ID (defaults to eleven_turbo_v2_5)
            voice_a: Voice ID for first speaker (Alex)
            voice_b: Voice ID for second speaker (Sam)
        """
        config = get_config()

        self.api_key = api_key or config.elevenlabs_api_key
        self.model_id = model_id or config.tts_model
        self.voice_a = voice_a or config.voice_a
        self.voice_b = voice_b or config.voice_b
        self.config = config

        if not self.api_key:
            raise ConfigurationError(
                "ElevenLabs API key is required for audio generation. "
                "Set ELEVENLABS_API_KEY environment variable or provide api_key parameter."
            )

        # Initialize ElevenLabs client
        try:
            self.client = ElevenLabs(api_key=self.api_key)
            logger.info("Initialized ElevenLabs client")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize ElevenLabs client: {e}")

        # Validate voices
        self._validate_voices()

        logger.info(
            f"Initialized ElevenLabs audio generator with model {self.model_id} and voices: {self.voice_a}, {self.voice_b}"  # noqa: E501
        )

    def _validate_voices(self) -> None:
        """Validate that the selected voices are available."""
        try:
            # Get available voices from ElevenLabs
            voices_response = self.client.voices.get_all()
            available_voices = [voice.voice_id for voice in voices_response.voices]

            if self.voice_a not in available_voices:
                logger.warning(
                    f"Voice A '{self.voice_a}' may not be available. Available voices: {available_voices[:10]}..."
                )
            if self.voice_b not in available_voices:
                logger.warning(
                    f"Voice B '{self.voice_b}' may not be available. Available voices: {available_voices[:10]}..."
                )

        except Exception as e:
            logger.warning(f"Could not validate voices: {e}")

    def generate_audio(
        self, script: str, output_file: Optional[Path] = None
    ) -> AudioResult:
        """
        Generate audio from a podcast script using ElevenLabs Text-to-Speech.

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
            # Parse and prepare script for multi-speaker TTS
            speaker_segments = self._parse_script_for_speakers(script)

            if not speaker_segments:
                raise AudioGenerationError("No dialogue found in script")

            logger.info(f"Parsed script into {len(speaker_segments)} speaker segments")

            # Generate audio using ElevenLabs individual voice synthesis
            audio_data = self._generate_with_individual_voices(speaker_segments)

            # Save the audio file
            self._save_audio(audio_data, output_file)

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

    def _parse_script_for_speakers(self, script: str) -> List[Dict[str, str]]:
        """Parse script and identify speaker segments."""
        lines = script.split("\n")
        segments: List[Dict[str, str]] = []

        for line in lines:
            line = line.strip()

            # Skip empty lines, headers, and formatting
            if not line or line.startswith("#") or line.startswith("**"):
                continue

            # Handle dialogue lines
            if line.startswith("Alex:"):
                content = line[5:].strip()
                segments.append(
                    {"text": content, "speaker": "Alex", "voice": self.voice_a}
                )
            elif line.startswith("Sam:"):
                content = line[4:].strip()
                segments.append(
                    {"text": content, "speaker": "Sam", "voice": self.voice_b}
                )
            else:
                # Non-dialogue text - assign to Alex by default
                if line:
                    segments.append(
                        {"text": line, "speaker": "Alex", "voice": self.voice_a}
                    )

        return segments

    def _generate_with_individual_voices(self, segments: List[Dict[str, str]]) -> bytes:
        """Generate audio using ElevenLabs individual voice synthesis and combine."""
        audio_chunks: List[bytes] = []

        for i, segment in enumerate(segments):
            try:
                # Select the appropriate voice for this segment
                voice_id = segment["voice"]
                text = segment["text"]

                # Add pauses and improve text for ElevenLabs
                if i > 0:  # Add small pause before non-first segments
                    text = f"<break time='0.3s'/>{text}"

                # Generate audio using ElevenLabs
                response = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id=self.model_id,
                    output_format="mp3_44100_192",  # High quality for Creator tier
                    voice_settings=VoiceSettings(
                        stability=0.5,  # Balanced for dialogue
                        similarity_boost=0.75,  # Good voice consistency
                        style=0.2,  # Slight style variation
                        use_speaker_boost=True,  # Better multi-speaker clarity
                    ),
                )

                # Convert generator to bytes
                if response:
                    audio_bytes = b"".join(response)  # Consume the generator
                    audio_chunks.append(audio_bytes)
                    logger.debug(
                        f"Generated segment {i+1}/{len(segments)} ({len(audio_bytes)} bytes)"
                    )
                else:
                    logger.warning(f"No audio content for segment {i+1}")

            except Exception as e:
                logger.warning(f"Failed to generate audio for segment {i+1}: {e}")
                continue

        if not audio_chunks:
            raise AudioGenerationError("No audio segments were successfully generated")

        # Combine all audio chunks (MP3 concatenation)
        return b"".join(audio_chunks)

    def _save_audio(self, audio_data: bytes, output_file: Path) -> None:
        """Save MP3 audio data to file."""
        try:
            # ElevenLabs returns complete MP3 data, save directly
            with open(output_file, "wb") as f:
                f.write(audio_data)
            logger.info(f"Saved MP3 audio to {output_file}")

        except Exception as e:
            raise AudioGenerationError(f"Failed to save audio to {output_file}: {e}")

    def get_available_voices(self) -> Dict[str, List[str]]:
        """Get available voices from ElevenLabs."""
        try:
            response = self.client.voices.get_all()

            voices_by_gender: Dict[str, List[str]] = {"male": [], "female": []}
            for voice in response.voices:
                # ElevenLabs voices don't have explicit gender markers
                # For now, categorize by voice ID (this could be improved)
                voices_by_gender["male"].append(voice.voice_id)

            return voices_by_gender

        except Exception as e:
            logger.warning(f"Could not retrieve available voices: {e}")
            # Return default voices for compatibility
            return self.DEFAULT_VOICES

    def test_authentication(self) -> bool:
        """Test ElevenLabs authentication and basic functionality."""
        try:
            # Try to get voices to test authentication
            voices = self.client.voices.get_all()

            if voices:
                logger.info("Authentication successful! Retrieved voice list.")
                return True
            else:
                logger.warning("Authentication successful but no voices found")
                return False

        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False
