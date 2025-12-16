"""Audio generation using Google Gemini TTS."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

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
    """Generates podcast audio from scripts using Gemini TTS."""

    # Available voices for multi-speaker TTS
    AVAILABLE_VOICES = {
        "puck": "Energetic and dynamic",
        "charon": "Deep and authoritative",
        "kore": "Warm and conversational",
        "fenrir": "Rich and engaging",
        "aoede": "Clear and professional",
        "zephyr": "Natural and balanced",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_a: Optional[str] = None,
        voice_b: Optional[str] = None,
    ):
        """
        Initialize the audio generator.

        Args:
            api_key: Google API key (defaults to config)
            voice_a: Voice for first speaker (defaults to config)
            voice_b: Voice for second speaker (defaults to config)
        """
        config = get_config()

        self.api_key = api_key or config.google_api_key
        if not self.api_key:
            raise ConfigurationError("Google API key is required for audio generation")

        self.voice_a = (voice_a or config.voice_a).lower()
        self.voice_b = (voice_b or config.voice_b).lower()
        self.config = config

        # Validate voices
        if self.voice_a not in self.AVAILABLE_VOICES:
            raise ConfigurationError(
                f"Voice A '{self.voice_a}' not available. Options: {list(self.AVAILABLE_VOICES.keys())}"
            )
        if self.voice_b not in self.AVAILABLE_VOICES:
            raise ConfigurationError(
                f"Voice B '{self.voice_b}' not available. Options: {list(self.AVAILABLE_VOICES.keys())}"
            )

        # Configure Gemini client
        self.client = genai.Client(api_key=self.api_key)

        logger.info(
            f"Initialized audio generator with voices: {self.voice_a}, {self.voice_b}"
        )

    def generate_audio(
        self, script: str, output_file: Optional[Path] = None
    ) -> AudioResult:
        """
        Generate audio from a podcast script.

        Args:
            script: Podcast script text
            output_file: Output file path (defaults to config output directory)

        Returns:
            AudioResult with generation details

        Raises:
            AudioGenerationError: If audio generation fails
            ValidationError: If script is invalid
        """
        if not script or len(script.strip()) < 100:
            raise AudioGenerationError("Script too short or empty")

        if output_file is None:
            output_file = self.config.output_directory / "episode.wav"

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating audio to {output_file}")
        start_time = datetime.now()

        try:
            # Prepare script for TTS
            tts_script = self._prepare_script_for_tts(script)

            # Generate audio using Gemini
            audio_data = self._generate_with_gemini(tts_script)

            # Save audio file
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

    def _prepare_script_for_tts(self, script: str) -> str:
        """Prepare script for TTS by adding voice tags."""
        lines = script.split("\n")
        tts_lines = []

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith("#"):
                continue

            # Handle dialogue lines
            if line.startswith("Alex:"):
                content = line[5:].strip()
                tts_lines.append(
                    f'<speak><voice name="{self.voice_a}">{content}</voice></speak>'
                )
            elif line.startswith("Sam:"):
                content = line[4:].strip()
                tts_lines.append(
                    f'<speak><voice name="{self.voice_b}">{content}</voice></speak>'
                )
            else:
                # Non-dialogue text - use default voice
                if line and not line.startswith("**"):  # Skip formatting lines
                    tts_lines.append(
                        f'<speak><voice name="{self.voice_a}">{line}</voice></speak>'
                    )

        if not tts_lines:
            raise AudioGenerationError("No dialogue found in script")

        return "\n\n".join(tts_lines)

    def _generate_with_gemini(self, tts_script: str) -> bytes:
        """Generate audio using Gemini TTS."""
        try:
            # Generate audio
            response = self.client.models.generate_content(
                contents=tts_script,
                model=self.config.gemini_model,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower for more consistent audio
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                            speaker_voice_configs=[
                                types.SpeakerVoiceConfig(
                                    speaker="Alex",
                                    voice_config=types.VoiceConfig(
                                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                            voice_name=self.voice_a,
                                        )
                                    ),
                                ),
                                types.SpeakerVoiceConfig(
                                    speaker="Sam",
                                    voice_config=types.VoiceConfig(
                                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                            voice_name=self.voice_b,
                                        )
                                    ),
                                ),
                            ]
                        )
                    ),
                ),
            )

            if not response.candidates:
                raise AudioGenerationError("No audio generated by Gemini")

            # Extract audio data
            candidate = response.candidates[0]
            if (
                not hasattr(candidate, "content")
                or candidate.content is None
                or not candidate.content.parts
            ):
                raise AudioGenerationError("No audio content in Gemini response")

            # Get audio bytes (this is a simplified version - actual implementation depends on Gemini API)
            audio_part = candidate.content.parts[0]
            if (
                hasattr(audio_part, "inline_data")
                and audio_part.inline_data is not None
                and hasattr(audio_part.inline_data, "data")
            ):
                inline_data = getattr(audio_part, "inline_data", None)
                if inline_data is not None and hasattr(inline_data, "data"):
                    data = inline_data.data
                    if isinstance(data, bytes):
                        return data
                    else:
                        raise AudioGenerationError("Audio data is not in bytes format")
                else:
                    raise AudioGenerationError("No inline_data found in response")
            else:
                raise AudioGenerationError("No audio data found in response")

        except Exception as e:
            if isinstance(e, AudioGenerationError):
                raise
            raise AudioGenerationError(f"Gemini TTS generation failed: {e}")

    def _save_audio(self, audio_data: bytes, output_file: Path) -> None:
        """Save audio data to file with proper WAV format."""
        import wave

        try:
            # Check if data is already a valid WAV file by looking for RIFF header
            if (
                len(audio_data) >= 12
                and audio_data[:4] == b"RIFF"
                and audio_data[8:12] == b"WAVE"
            ):
                # Already a valid WAV file, save directly
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                logger.debug(f"Valid WAV data saved directly to {output_file}")
                return

            # Not a WAV file, assume it's raw PCM data that needs conversion
            # Skip any null padding at the beginning
            start_idx = 0
            while (
                start_idx < len(audio_data)
                and audio_data[start_idx : start_idx + 2] == b"\x00\x00"
            ):
                start_idx += 2

            # Get the actual audio data
            actual_audio_data = audio_data[start_idx:]

            if not actual_audio_data:
                raise AudioGenerationError(
                    "No valid audio data found after skipping padding"
                )

            # Create WAV file with proper headers for raw PCM data
            with wave.open(str(output_file), "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)  # Sample rate (adjust as needed)
                wav_file.writeframes(actual_audio_data)

            logger.debug(f"Raw PCM data converted and saved to {output_file}")

        except Exception as e:
            raise AudioGenerationError(f"Failed to save audio to {output_file}: {e}")

    def get_available_voices(self) -> dict:
        """Get available voices and their descriptions."""
        return self.AVAILABLE_VOICES.copy()
