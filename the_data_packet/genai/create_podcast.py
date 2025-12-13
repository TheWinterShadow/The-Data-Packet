"""
Gemini 2.5 TTS Audio Generator
Converts podcast scripts into audio using Gemini 2.5's native multi-speaker TTS.
"""

import os
import wave
import struct
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from google import genai
from google.genai import types


class GeminiPodcastTTS:
    """
    Generate podcast audio from scripts using Gemini 2.5 TTS.

    Supports:
    - Multi-speaker dialogue (Alex and Sam)
    - Natural pacing and intonation
    - Multiple voice options
    - Automatic chunking for long scripts
    """

    # Available Gemini voices for multi-speaker TTS
    AVAILABLE_VOICES = {
        "puck": "Puck - Energetic and dynamic",
        "charon": "Charon - Deep and authoritative",
        "kore": "Kore - Warm and conversational",
        "fenrir": "Fenrir - Rich and engaging",
        "aoede": "Aoede - Clear and professional",
        "zephyr": "Zephyr - Natural and balanced"
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-pro-preview-tts",
        voice_a: str = "Puck",
        voice_b: str = "Kore"
    ):
        """
        Initialize the TTS generator.

        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY or GOOGLE_API_KEY env var)
            model: Gemini model to use (default: "gemini-2.5-pro-preview-tts")
            voice_a: Voice for Alex (default: "Puck")
            voice_b: Voice for Sam (default: "Kore")
        """
        self.api_key = api_key or os.environ.get(
            "GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set GEMINI_API_KEY or GOOGLE_API_KEY env var or pass api_key parameter.")

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model

        # Voice configuration
        self.voice_a = voice_a
        self.voice_b = voice_b

        print(f"✅ Initialized Gemini TTS")
        print(f"   Model: {model}")
        print(f"   Voice A (Alex): {voice_a}")
        print(f"   Voice B (Sam): {voice_b}")

    def generate_audio(
        self,
        script: str,
        output_file: str = "podcast_episode.wav",
        sample_rate: int = 24000,
        chunk_size: int = 8000
    ) -> str:
        """
        Generate audio from podcast script.

        Args:
            script: TTS-formatted podcast script with speaker labels (Alex: / Sam:)
            output_file: Output audio file path
            sample_rate: Audio sample rate (default: 24000 Hz)
            chunk_size: Maximum characters per API call (default: 8000)

        Returns:
            Path to generated audio file
        """
        print(f"\n🎙️  Generating podcast audio...")
        print(f"📄 Script length: {len(script)} characters")

        # Check if script needs chunking
        if len(script) > chunk_size:
            print(f"⚠️  Script is long, will process in chunks...")
            return self._generate_chunked_audio(script, output_file, chunk_size)
        else:
            return self._generate_single_audio(script, output_file)

    def _generate_single_audio(
        self,
        script: str,
        output_file: str
    ) -> str:
        """Generate audio in a single API call."""

        print(f"🔄 Generating audio...")

        # Convert script to Gemini format
        formatted_script = self._format_script_for_gemini(script)

        try:
            # Set up multi-speaker configuration
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=formatted_script),
                    ],
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

            # Generate audio with streaming
            audio_chunks = []
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue

                # Extract audio data from chunk
                if (chunk.candidates[0].content.parts[0].inline_data and
                        chunk.candidates[0].content.parts[0].inline_data.data):
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    audio_chunks.append(
                        (inline_data.data, inline_data.mime_type))

            # Combine all audio chunks
            if not audio_chunks:
                raise ValueError("No audio data generated")

            # Convert to WAV and save
            self._save_audio_chunks(audio_chunks, output_file)

            print(f"✅ Audio generated: {output_file}")
            return output_file

        except Exception as e:
            print(f"❌ Error generating audio: {e}")
            raise

    def _generate_chunked_audio(
        self,
        script: str,
        output_file: str,
        chunk_size: int
    ) -> str:
        """Generate audio in chunks and combine."""

        # Split script into chunks
        chunks = self._split_script(script, chunk_size)
        print(f"📊 Split into {len(chunks)} chunks")

        # Generate audio for each chunk
        chunk_files = []
        for i, chunk in enumerate(chunks, 1):
            print(f"\n🔄 Processing chunk {i}/{len(chunks)}...")

            chunk_file = f"temp_chunk_{i:03d}.wav"

            try:
                self._generate_single_audio(chunk, chunk_file)
                chunk_files.append(chunk_file)
                print(f"✅ Chunk {i} complete")

            except Exception as e:
                print(f"❌ Error on chunk {i}: {e}")
                # Clean up any created files
                for cf in chunk_files:
                    if os.path.exists(cf):
                        os.remove(cf)
                raise

        # Combine all chunks
        print(f"\n🔧 Combining {len(chunk_files)} chunks...")
        self._combine_wav_files(chunk_files, output_file)

        # Clean up temporary files
        for chunk_file in chunk_files:
            if os.path.exists(chunk_file):
                os.remove(chunk_file)

        print(f"✅ Audio generated: {output_file}")
        return output_file

    def _format_script_for_gemini(self, script: str) -> str:
        """
        Format script for Gemini TTS API.

        Adds instruction to read the script as a podcast conversation.

        Args:
            script: Script with Alex: and Sam: labels

        Returns:
            Formatted script with instructions
        """
        formatted = f"""Please read aloud the following in a podcast interview style with natural conversation flow:

{script}"""
        return formatted

    def _save_audio_chunks(self, audio_chunks: List[tuple], output_file: str):
        """
        Save audio chunks to WAV file.

        Args:
            audio_chunks: List of (data, mime_type) tuples
            output_file: Output file path
        """
        # Combine all audio data
        all_audio_data = b""
        mime_type = None

        for data, mime in audio_chunks:
            all_audio_data += data
            if mime_type is None:
                mime_type = mime

        # Convert to WAV format
        wav_data = self._convert_to_wav(all_audio_data, mime_type)

        # Save to file
        with open(output_file, "wb") as f:
            f.write(wav_data)

    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """
        Convert audio data to WAV format.

        Args:
            audio_data: Raw audio data
            mime_type: MIME type of audio data

        Returns:
            WAV formatted audio data
        """
        # Parse audio parameters from MIME type
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size

        # Create WAV header
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",          # ChunkID
            chunk_size,       # ChunkSize
            b"WAVE",          # Format
            b"fmt ",          # Subchunk1ID
            16,               # Subchunk1Size (16 for PCM)
            1,                # AudioFormat (1 for PCM)
            num_channels,     # NumChannels
            sample_rate,      # SampleRate
            byte_rate,        # ByteRate
            block_align,      # BlockAlign
            bits_per_sample,  # BitsPerSample
            b"data",          # Subchunk2ID
            data_size         # Subchunk2Size
        )

        return header + audio_data

    def _parse_audio_mime_type(self, mime_type: str) -> dict:
        """
        Parse audio parameters from MIME type.

        Args:
            mime_type: Audio MIME type (e.g., "audio/L16;rate=24000")

        Returns:
            Dictionary with bits_per_sample and rate
        """
        bits_per_sample = 16
        rate = 24000

        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass

        return {"bits_per_sample": bits_per_sample, "rate": rate}

    def _split_script(self, script: str, chunk_size: int) -> List[str]:
        """
        Split script into chunks at natural dialogue breaks.

        Args:
            script: Full script text
            chunk_size: Target chunk size in characters

        Returns:
            List of script chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0

        # Split by paragraphs (double newline)
        paragraphs = script.split('\n\n')

        for para in paragraphs:
            para_size = len(para)

            # If adding this paragraph exceeds chunk size, start new chunk
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def _combine_wav_files(
        self,
        input_files: List[str],
        output_file: str
    ):
        """
        Combine multiple WAV files into one.

        Args:
            input_files: List of input WAV file paths
            output_file: Output file path
        """
        with wave.open(output_file, 'wb') as output:
            # Set parameters from first file
            with wave.open(input_files[0], 'rb') as first:
                params = first.getparams()
                output.setparams(params)

            # Append all files
            for input_file in input_files:
                with wave.open(input_file, 'rb') as input_wav:
                    output.writeframes(
                        input_wav.readframes(input_wav.getnframes())
                    )

    def generate_from_file(
        self,
        script_file: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate audio from script file.

        Args:
            script_file: Path to TTS script file
            output_file: Optional output file path

        Returns:
            Path to generated audio file
        """
        print(f"📂 Reading script from: {script_file}")

        # Read script
        with open(script_file, 'r', encoding='utf-8') as f:
            script = f.read()

        # Generate output filename if not provided
        if output_file is None:
            script_path = Path(script_file)
            output_file = script_path.stem + ".wav"

        # Generate audio
        return self.generate_audio(script, output_file)

    def estimate_duration(self, script: str) -> float:
        """
        Estimate audio duration in minutes.

        Rough estimate: ~150 words per minute of speech

        Args:
            script: Script text

        Returns:
            Estimated duration in minutes
        """
        # Count words
        words = len(script.split())

        # Estimate duration (150 words per minute)
        duration_minutes = words / 150

        return duration_minutes


def main():
    """Command-line interface for TTS generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate podcast audio from script using Gemini 2.5 TTS"
    )
    parser.add_argument(
        "script_file",
        help="Path to TTS-formatted script file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output audio file path (default: script_name.wav)"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-pro-preview-tts",
        help="Gemini model to use (default: gemini-2.5-pro-preview-tts)"
    )
    parser.add_argument(
        "--voice-a",
        default="Puck",
        help="Voice for Alex (default: Puck)"
    )
    parser.add_argument(
        "--voice-b",
        default="Kore",
        help="Voice for Sam (default: Kore)"
    )
    parser.add_argument(
        "--api-key",
        help="Google API key (or set GEMINI_API_KEY env var)"
    )

    args = parser.parse_args()

    try:
        # Initialize TTS generator
        tts = GeminiPodcastTTS(
            api_key=args.api_key,
            model=args.model,
            voice_a=args.voice_a,
            voice_b=args.voice_b
        )

        # Generate audio
        output_file = tts.generate_from_file(
            script_file=args.script_file,
            output_file=args.output
        )

        print(f"\n✅ Success! Audio saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0
