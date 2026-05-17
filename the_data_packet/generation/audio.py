"""Audio generation using Vertex AI Gemini TTS."""

import tempfile
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    HttpOptions,
    PrebuiltVoiceConfig,
    SpeechConfig,
    VoiceConfig,
)

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
    """Generates podcast audio from scripts using Vertex AI Gemini TTS."""

    AVAILABLE_VOICES = {"male": ["Puck"], "female": ["Kore"]}

    TTS_MODEL = "gemini-3.1-flash-tts-preview"
    SAMPLE_RATE = 24000  # Vertex AI TTS outputs 24kHz PCM

    def __init__(
        self,
        male_voice: Optional[str] = None,
        female_voice: Optional[str] = None,
        project: Optional[str] = None,
        location: str = "us-central1",
    ):
        config = get_config()

        self.male_voice = male_voice or getattr(config, "male_voice", "Puck")
        self.female_voice = female_voice or getattr(config, "female_voice", "Kore")
        self.project = project or getattr(config, "google_cloud_project", "gen-lang-client-0429374219")
        self.location = location
        self.config = config

        try:
            self.tts_client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location,
                http_options=HttpOptions(api_version="v1"),
            )
            logger.info("Initialized Vertex AI Gemini TTS client")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Vertex AI client: {e}")

        logger.info(
            f"Initialized Vertex AI TTS generator with voices: {self.male_voice} (Alex), {self.female_voice} (Sam)"
        )

    def _parse_script_to_turns(self, script: str) -> List[Tuple[str, str]]:
        """Parse script into (speaker, text) turns."""
        turns = []
        for line in script.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("**"):
                continue
            if line.startswith("Alex:"):
                turns.append(("Alex", line[5:].strip()))
            elif line.startswith("Sam:"):
                turns.append(("Sam", line[4:].strip()))
            elif line:
                turns.append(("Alex", line))
        return turns

    def _synthesize_turns(self, turns: List[Tuple[str, str]]) -> bytes:
        """Synthesize a list of (speaker, text) turns into combined PCM bytes."""
        combined_pcm = bytearray()

        for i, (speaker, text) in enumerate(turns):
            voice_name = self.male_voice if speaker == "Alex" else self.female_voice
            logger.info(f"  [{i + 1}/{len(turns)}] Synthesizing {speaker} using {voice_name}...")

            tts_config = GenerateContentConfig(
                temperature=0.7,
                speech_config=SpeechConfig(
                    voice_config=VoiceConfig(prebuilt_voice_config=PrebuiltVoiceConfig(voice_name=voice_name))
                ),
            )

            full_text = f"[short pause] {text}" if i > 0 else text

            try:
                response = self.tts_client.models.generate_content(
                    model=self.TTS_MODEL,
                    contents=full_text,
                    config=tts_config,
                )
                candidates = response.candidates or []
                content = candidates[0].content if candidates else None
                parts = content.parts if content is not None else None
                inline_data = parts[0].inline_data if parts else None
                if inline_data and inline_data.data:
                    combined_pcm.extend(inline_data.data)
                else:
                    logger.warning("Turn %d (%s) returned no audio data", i + 1, speaker)

                time.sleep(0.5)

            except Exception as e:
                logger.error("Error synthesizing turn %d (%s): %s", i + 1, speaker, e)
                raise AudioGenerationError(f"Failed to synthesize turn {i + 1}: {e}") from e

        return bytes(combined_pcm)

    def generate_audio(self, script: str, output_file: Optional[Path] = None) -> AudioResult:
        """Generate audio from a podcast script."""
        if not script or len(script.strip()) < 100:
            raise AudioGenerationError("Script too short or empty")

        if output_file is None:
            output_file = self.config.output_directory / "episode.mp3"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        turns = self._parse_script_to_turns(script)
        if not turns:
            raise AudioGenerationError("No speakable turns found in script")

        logger.info(f"Synthesizing {len(turns)} turns with Vertex AI TTS...")
        pcm_data = self._synthesize_turns(turns)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            with wave.open(str(tmp_path), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.SAMPLE_RATE)
                wav_file.writeframes(pcm_data)

            self.convert_wav_to_mp3(tmp_path, output_file)
        finally:
            try:
                tmp_path.unlink()
            except Exception:
                pass

        file_size = output_file.stat().st_size if output_file.exists() else None
        logger.info(f"Audio generated at {output_file}")
        return AudioResult(output_file=output_file, file_size_bytes=file_size)

    def get_available_voices(self) -> Dict[str, List[str]]:
        """Get available Vertex AI TTS voices."""
        return {k: list(v) for k, v in self.AVAILABLE_VOICES.items()}

    def convert_wav_to_mp3(self, wav_path: Path, mp3_path: Path) -> None:
        """Convert a wav file to mp3 using pydub."""
        from pydub import AudioSegment

        audio = AudioSegment.from_wav(wav_path)
        audio.export(mp3_path, format="mp3")
        logger.info(f"Converted {wav_path} to {mp3_path}")
