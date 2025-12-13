"""
Enhanced Gemini TTS Audio Generator
Converts podcast scripts into audio using Gemini 2.5's native multi-speaker TTS.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from google import genai
from google.genai import types

from the_data_packet.config import get_settings
from the_data_packet.core.exceptions import AudioGenerationError, ValidationError
from the_data_packet.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class AudioGenerationResult:
    """Result of audio generation operation."""

    output_file: Path
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    generation_time_seconds: Optional[float] = None
    chunks_generated: int = 1


class GeminiTTSGenerator:
    """
    Enhanced generator for podcast audio from scripts using Gemini 2.5 TTS.

    Features:
    - Multi-speaker dialogue (Alex and Sam)
    - Natural pacing and intonation
    - Multiple voice options
    - Automatic chunking for long scripts
    - Comprehensive error handling
    - Progress tracking
    """

    # Available Gemini voices for multi-speaker TTS
    AVAILABLE_VOICES = {
        "puck": "Puck - Energetic and dynamic",
        "charon": "Charon - Deep and authoritative",
        "kore": "Kore - Warm and conversational",
        "fenrir": "Fenrir - Rich and engaging",
        "aoede": "Aoede - Clear and professional",
        "zephyr": "Zephyr - Natural and balanced",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        voice_a: Optional[str] = None,
        voice_b: Optional[str] = None,
    ):
        """
        Initialize the TTS generator.

        Args:
            api_key: Google API key (defaults to settings)
            model: Gemini model to use (defaults to settings)
            voice_a: Voice for Alex (defaults to settings)
            voice_b: Voice for Sam (defaults to settings)
        """
        settings = get_settings()

        self.api_key = api_key or settings.google_api_key
        if not self.api_key:
            raise AudioGenerationError(
                "Google API key is required for TTS. Set GOOGLE_API_KEY or GEMINI_API_KEY env var."
            )

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model or settings.gemini_model

        # Voice configuration
        self.voice_a = voice_a or settings.default_voice_a
        self.voice_b = voice_b or settings.default_voice_b

        # Audio settings
        self.sample_rate = settings.audio_sample_rate
        self.chunk_size = settings.audio_chunk_size

        logger.info(f"Initialized Gemini TTS Generator")
        logger.info(f"Model: {self.model_name}")
        logger.info(f"Voice A (Alex): {self.voice_a}")
        logger.info(f"Voice B (Sam): {self.voice_b}")

    def generate_audio(
        self, script: str, output_file: Union[str, Path] = "podcast_episode.wav"
    ) -> AudioGenerationResult:
        """
        Generate audio from podcast script.

        Args:
            script: TTS-formatted podcast script with speaker labels (Alex: / Sam:)
            output_file: Output audio file path

        Returns:
            AudioGenerationResult with metadata

        Raises:
            AudioGenerationError: If generation fails
            ValidationError: If script is invalid
        """
        if not script or not script.strip():
            raise ValidationError("Script cannot be empty")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        start_time = datetime.now()

        logger.info(f"Generating podcast audio...")
        logger.info(f"Script length: {len(script)} characters")
        logger.info(f"Output file: {output_path}")

        try:
            # Check if script needs chunking
            if len(script) > self.chunk_size:
                logger.info(
                    f"Script is long, processing in chunks (max {self.chunk_size} chars each)"
                )
                result = self._generate_chunked_audio(script, output_path)
            else:
                result = self._generate_single_audio(script, output_path)

            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            result.generation_time_seconds = generation_time

            # Get file size
            if output_path.exists():
                result.file_size_bytes = output_path.stat().st_size

            logger.info(f"Successfully generated audio in {generation_time:.1f}s")
            logger.info(
                f"Output file: {result.output_file} ({result.file_size_bytes} bytes)"
            )

            return result

        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise AudioGenerationError(f"Failed to generate audio: {e}") from e

    def _generate_single_audio(
        self, script: str, output_file: Path
    ) -> AudioGenerationResult:
        """Generate audio in a single API call."""
        logger.debug("Generating audio in single call")

        # Convert script to Gemini format
        formatted_script = self._format_script_for_gemini(script)

        try:
            # Set up multi-speaker configuration
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=formatted_script)],
                ),
            ]

            config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker="Alex",
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=self.voice_a
                                    )
                                ),
                            ),
                            types.SpeakerVoiceConfig(
                                speaker="Sam",
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=self.voice_b
                                    )
                                ),
                            ),
                        ]
                    ),
                ),
            )

            # Generate audio
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            if not response.candidates:
                raise AudioGenerationError("No audio candidates in response")

            # Extract audio data
            audio_data = response.candidates[0].content.parts[0].inline_data.data

            # Save as WAV file
            self._save_wav_file(audio_data, output_file)

            return AudioGenerationResult(output_file=output_file, chunks_generated=1)

        except Exception as e:
            logger.error(f"Error in single audio generation: {e}")
            raise AudioGenerationError(f"Single audio generation failed: {e}") from e

    def _generate_chunked_audio(
        self, script: str, output_file: Path
    ) -> AudioGenerationResult:
        """Generate audio in chunks and combine them."""
        logger.info("Processing script in chunks")

        # Split script into chunks
        chunks = self._split_script_into_chunks(script)
        logger.info(f"Split script into {len(chunks)} chunks")

        audio_segments = []

        try:
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")

                # Generate audio for this chunk
                temp_file = output_file.parent / f"temp_chunk_{i}.wav"
                result = self._generate_single_audio(chunk, temp_file)

                # Read the audio data
                with open(temp_file, "rb") as f:
                    audio_data = f.read()
                    audio_segments.append(audio_data)

                # Clean up temp file
                temp_file.unlink(missing_ok=True)

            # Combine all audio segments
            self._combine_audio_segments(audio_segments, output_file)

            return AudioGenerationResult(
                output_file=output_file, chunks_generated=len(chunks)
            )

        except Exception as e:
            logger.error(f"Error in chunked audio generation: {e}")
            # Clean up any temp files
            for i in range(len(chunks)):
                temp_file = output_file.parent / f"temp_chunk_{i}.wav"
                temp_file.unlink(missing_ok=True)
            raise AudioGenerationError(f"Chunked audio generation failed: {e}") from e

    def _split_script_into_chunks(self, script: str) -> List[str]:
        """
        Split script into chunks at natural break points.

        Args:
            script: Full script text

        Returns:
            List of script chunks
        """
        if len(script) <= self.chunk_size:
            return [script]

        chunks = []
        lines = script.split("\n")
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line) + 1  # +1 for newline

            # If adding this line would exceed chunk size, start a new chunk
            if current_size + line_size > self.chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        # Add the last chunk
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _format_script_for_gemini(self, script: str) -> str:
        """
        Format script text for Gemini TTS processing.

        Args:
            script: Raw script text

        Returns:
            Formatted script with proper speaker labels
        """
        # Ensure proper speaker formatting
        lines = script.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("")
                continue

            # Ensure speaker labels are properly formatted
            if line.startswith("Alex:") or line.startswith("Sam:"):
                formatted_lines.append(line)
            elif ":" in line and line.split(":")[0].strip() in ["Alex", "Sam"]:
                # Fix formatting if needed
                speaker, content = line.split(":", 1)
                formatted_lines.append(f"{speaker.strip()}: {content.strip()}")
            else:
                # If no speaker label, assume Alex
                formatted_lines.append(f"Alex: {line}")

        return "\n".join(formatted_lines)

    def _save_wav_file(self, audio_data: bytes, output_file: Path) -> None:
        """
        Save raw audio data as WAV file.

        Args:
            audio_data: Raw audio bytes
            output_file: Output file path
        """
        try:
            with open(output_file, "wb") as f:
                f.write(audio_data)

            logger.debug(f"Saved WAV file: {output_file}")

        except Exception as e:
            logger.error(f"Error saving WAV file: {e}")
            raise AudioGenerationError(f"Failed to save audio file: {e}") from e

    def _combine_audio_segments(self, segments: List[bytes], output_file: Path) -> None:
        """
        Combine multiple audio segments into a single WAV file.

        Args:
            segments: List of audio data segments
            output_file: Output file path
        """
        if not segments:
            raise AudioGenerationError("No audio segments to combine")

        try:
            # Simple concatenation for now - could be improved with proper audio mixing
            combined_data = b"".join(segments)

            with open(output_file, "wb") as f:
                f.write(combined_data)

            logger.debug(f"Combined {len(segments)} audio segments")

        except Exception as e:
            logger.error(f"Error combining audio segments: {e}")
            raise AudioGenerationError(f"Failed to combine audio segments: {e}") from e

    @classmethod
    def list_available_voices(cls) -> Dict[str, str]:
        """Get available voice options."""
        return cls.AVAILABLE_VOICES.copy()

    def validate_voices(self) -> bool:
        """
        Validate that selected voices are available.

        Returns:
            True if voices are valid
        """
        available = set(self.AVAILABLE_VOICES.keys())
        selected = {self.voice_a.lower(), self.voice_b.lower()}

        if not selected.issubset(available):
            invalid = selected - available
            logger.warning(f"Invalid voices selected: {invalid}")
            return False

        return True
