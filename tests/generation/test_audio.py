"""Unit tests for generation.audio module."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from the_data_packet.core.exceptions import AudioGenerationError, ConfigurationError
from the_data_packet.generation.audio import AudioGenerator, AudioResult


class TestAudioResult(unittest.TestCase):
    """Test cases for AudioResult dataclass."""

    def test_audio_result_creation(self):
        """Test AudioResult creation with minimum required fields."""
        result = AudioResult(output_file=Path("test.mp3"))

        self.assertEqual(result.output_file, Path("test.mp3"))
        self.assertIsNone(result.duration_seconds)
        self.assertIsNone(result.file_size_bytes)
        self.assertIsNone(result.generation_time_seconds)

    def test_audio_result_with_all_fields(self):
        """Test AudioResult creation with all fields."""
        result = AudioResult(
            output_file=Path("test.mp3"),
            duration_seconds=120.5,
            file_size_bytes=1024000,
            generation_time_seconds=45.2,
        )

        self.assertEqual(result.output_file, Path("test.mp3"))
        self.assertEqual(result.duration_seconds, 120.5)
        self.assertEqual(result.file_size_bytes, 1024000)
        self.assertEqual(result.generation_time_seconds, 45.2)


class TestAudioGenerator(unittest.TestCase):
    """Test cases for AudioGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.gcs_bucket_name = "test-audio-bucket"
        self.mock_config.google_credentials_path = None  # No credentials file in tests
        self.mock_config.male_voice = "en-US-Studio-Q"
        self.mock_config.female_voice = "en-US-Studio-O"
        self.mock_config.output_directory = Path("/tmp/test")
        self.mock_config.cleanup_temp_files = True

    def test_available_voices_defined(self):
        """Test that available voices are properly defined."""
        self.assertIsInstance(AudioGenerator.AVAILABLE_VOICES, dict)
        self.assertIn("male", AudioGenerator.AVAILABLE_VOICES)
        self.assertIn("female", AudioGenerator.AVAILABLE_VOICES)
        self.assertIn("en-US-Studio-Q", AudioGenerator.AVAILABLE_VOICES["male"])
        self.assertIn("en-US-Studio-O", AudioGenerator.AVAILABLE_VOICES["female"])

    def test_audio_config_defined(self):
        """Test that audio configuration is properly defined."""
        from google.cloud import texttospeech

        self.assertIsInstance(AudioGenerator.AUDIO_CONFIG, dict)
        self.assertEqual(
            AudioGenerator.AUDIO_CONFIG["audio_encoding"],
            texttospeech.AudioEncoding.LINEAR16,
        )
        self.assertEqual(AudioGenerator.AUDIO_CONFIG["sample_rate_hertz"], 44100)

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_init_with_gcs_bucket(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test AudioGenerator initialization with GCS bucket."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True
        mock_tts_client = Mock()
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []
        mock_tts.return_value = mock_tts_client
        mock_storage.return_value = mock_storage_client

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        self.assertEqual(generator.gcs_bucket_name, "test-bucket")
        self.assertEqual(generator.male_voice, "en-US-Studio-Q")
        self.assertEqual(generator.female_voice, "en-US-Studio-O")

    @patch("the_data_packet.generation.audio.get_config")
    def test_init_without_gcs_bucket_raises_error(self, mock_get_config):
        """Test that initialization without GCS bucket raises ConfigurationError."""
        mock_config_no_bucket = Mock()
        mock_config_no_bucket.gcs_bucket_name = None
        mock_get_config.return_value = mock_config_no_bucket

        with self.assertRaises(ConfigurationError) as cm:
            AudioGenerator()

        self.assertIn("Google Cloud Storage bucket is required", str(cm.exception))

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_init_with_custom_voices(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test AudioGenerator initialization with custom voices."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True
        mock_tts_client = Mock()
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []
        mock_tts.return_value = mock_tts_client
        mock_storage.return_value = mock_storage_client

        generator = AudioGenerator(
            gcs_bucket_name="test-bucket",
            male_voice="en-US-Studio-Q",
            female_voice="Leda",
        )

        self.assertEqual(generator.male_voice, "en-US-Studio-Q")
        self.assertEqual(generator.female_voice, "Leda")

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_validate_gcs_bucket_success(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test successful GCS bucket validation."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []
        mock_storage.return_value = mock_storage_client
        mock_tts.return_value = Mock()

        # Should not raise an exception
        generator = AudioGenerator(gcs_bucket_name="test-bucket")
        self.assertIsNotNone(generator)

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_generate_audio_with_empty_script_raises_error(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test that empty script raises AudioGenerationError."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []
        mock_storage.return_value = mock_storage_client
        mock_tts.return_value = Mock()

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        with self.assertRaises(AudioGenerationError) as cm:
            generator.generate_audio("")

        self.assertIn("Script too short or empty", str(cm.exception))

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_generate_audio_with_short_script_raises_error(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test that very short script raises AudioGenerationError."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []
        mock_storage.return_value = mock_storage_client
        mock_tts.return_value = Mock()

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        with self.assertRaises(AudioGenerationError) as cm:
            generator.generate_audio("Short")

        self.assertIn("Script too short or empty", str(cm.exception))

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_parse_script_to_ssml(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test script parsing to SSML with voice switching."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []
        mock_storage.return_value = mock_storage_client
        mock_tts.return_value = Mock()

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        script = """
        Alex: Welcome to the show!
        Sam: Thanks for having me.
        This is a narrator line.
        Alex: Let's talk about tech.
        """

        ssml = generator._parse_script_to_ssml(script)

        self.assertTrue(ssml.startswith("<speak>"))
        self.assertTrue(ssml.endswith("</speak>"))
        self.assertIn(
            '<voice name="en-US-Studio-Q">Welcome to the show!</voice>',
            ssml,
        )
        self.assertIn(
            '<voice name="en-US-Studio-O">Thanks for having me.</voice>',
            ssml,
        )
        self.assertIn(
            '<voice name="en-US-Studio-Q">This is a narrator line.</voice>',
            ssml,
        )
        self.assertIn(
            '<voice name="en-US-Studio-Q">Let\'s talk about tech.</voice>',
            ssml,
        )

    def test_get_available_voices_structure(self):
        """Test get_available_voices returns proper structure."""
        with patch("the_data_packet.generation.audio.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with (
                patch(
                    "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
                ),
                patch("the_data_packet.generation.audio.storage.Client"),
                patch("os.path.exists", return_value=True),
            ):

                mock_storage_client = Mock()
                mock_bucket = Mock()
                mock_storage_client.bucket.return_value = mock_bucket
                mock_bucket.list_blobs.return_value = []

                with patch(
                    "the_data_packet.generation.audio.storage.Client",
                    return_value=mock_storage_client,
                ):
                    generator = AudioGenerator(gcs_bucket_name="test-bucket")
                    voices = generator.get_available_voices()

                    self.assertIsInstance(voices, dict)
                    self.assertIn("male", voices)
                    self.assertIn("female", voices)
                    self.assertIn("en-US-Studio-Q", voices["male"])
                    self.assertIn("en-US-Studio-O", voices["female"])

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.texttospeech.TextToSpeechClient")
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_test_authentication_success(
        self, mock_exists, mock_storage, mock_tts_client, mock_tts_long, mock_get_config
    ):
        """Test successful authentication test."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock TTS client for authentication test
        mock_client = Mock()
        mock_voices_response = Mock()
        mock_voices_response.voices = [Mock()]  # Non-empty list
        mock_client.list_voices.return_value = mock_voices_response
        mock_tts_client.return_value = mock_client

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_bucket.exists.return_value = True
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage_client.bucket().list_blobs.return_value = []
        mock_storage.return_value = mock_storage_client

        # Mock long audio client
        mock_tts_long.return_value = Mock()

        generator = AudioGenerator(gcs_bucket_name="test-bucket")
        result = generator.test_authentication()

        self.assertTrue(result)

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.texttospeech.TextToSpeechClient")
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_test_authentication_failure(
        self, mock_exists, mock_storage, mock_tts_client, mock_tts_long, mock_get_config
    ):
        """Test failed authentication test."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock TTS client failure
        mock_client = Mock()
        mock_client.list_voices.side_effect = Exception("Auth failed")
        mock_tts_client.return_value = mock_client

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage_client.bucket().list_blobs.return_value = []
        mock_storage.return_value = mock_storage_client

        # Mock long audio client
        mock_tts_long.return_value = Mock()

        generator = AudioGenerator(gcs_bucket_name="test-bucket")
        result = generator.test_authentication()

        self.assertFalse(result)

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    @patch("time.sleep")
    def test_generate_audio_success(
        self, mock_sleep, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test successful audio generation with Google Cloud TTS."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock TTS long audio client
        mock_tts_client = Mock()
        mock_operation = Mock()
        mock_operation.operation.name = "test-operation"
        mock_operation.done.return_value = True
        mock_operation.result.return_value = Mock()
        mock_tts_client.synthesize_long_audio.return_value = mock_operation
        mock_tts.return_value = mock_tts_client

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        # Create a longer script to pass validation
        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI.
Alex: That's right. The latest developments are fascinating.
Sam: Absolutely. Let's dive into the details."""

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        # Mock generate_audio_chunked to avoid file system operations
        mock_result = AudioResult(
            output_file=Path("/tmp/test/episode.mp3"),
            duration_seconds=120.0,
            file_size_bytes=1024,
            generation_time_seconds=45.2,
        )

        with patch.object(
            generator, "generate_audio_chunked", return_value=mock_result
        ) as mock_chunked:
            result = generator.generate_audio(script)

            # Verify generate_audio_chunked was called
            mock_chunked.assert_called_once()
            self.assertIsInstance(result, AudioResult)
            self.assertEqual(result.output_file.name, "episode.mp3")
            self.assertIsNotNone(result.generation_time_seconds)
            self.assertEqual(result.file_size_bytes, 1024)

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_generate_audio_no_segments_found(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test audio generation when synthesis fails."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock TTS client failure
        mock_tts_client = Mock()
        mock_tts_client.synthesize_long_audio.side_effect = Exception("TTS failure")
        mock_tts.return_value = mock_tts_client

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI."""

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        with self.assertRaises(AudioGenerationError) as context:
            generator.generate_audio(script)

        self.assertIn(
            "Failed to generate audio with Google Cloud TTS", str(context.exception)
        )

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    @patch("time.sleep")
    def test_generate_audio_operation_timeout(
        self, mock_sleep, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test audio generation with operation timeout."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock TTS client with operation that never completes
        mock_tts_client = Mock()
        mock_operation = Mock()
        mock_operation.operation.name = "test-operation"
        mock_operation.done.return_value = False  # Never completes
        mock_tts_client.synthesize_long_audio.return_value = mock_operation
        mock_tts.return_value = mock_tts_client

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI."""

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        with self.assertRaises(AudioGenerationError) as context:
            generator.generate_audio(script)

        self.assertIn("Audio synthesis timed out", str(context.exception))

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_generate_audio_api_failure(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test audio generation with API failure."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock TTS client failure
        mock_tts_client = Mock()
        mock_tts_client.synthesize_long_audio.side_effect = Exception("API Error")
        mock_tts.return_value = mock_tts_client

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI."""

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        with self.assertRaises(AudioGenerationError) as context:
            generator.generate_audio(script)

        self.assertIn(
            "Failed to generate audio with Google Cloud TTS", str(context.exception)
        )

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    @patch("time.sleep")
    def test_download_audio_from_gcs_success(
        self, mock_sleep, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test successful audio download from GCS."""
        from pathlib import Path

        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        # Mock TTS client
        mock_tts.return_value = Mock()

        generator = AudioGenerator(gcs_bucket_name="test-bucket")
        gcs_uri = "gs://test-bucket/audio/episode_20231230_120000.mp3"
        output_file = Path("/test/output.mp3")

        generator._download_audio_from_gcs(gcs_uri, output_file)

        # Verify blob download was called
        mock_blob.download_to_filename.assert_called_once_with(str(output_file))

    def test_split_text_by_bytes(self):
        """Test text splitting by byte size."""
        with patch("the_data_packet.generation.audio.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with (
                patch(
                    "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
                ),
                patch("the_data_packet.generation.audio.storage.Client"),
                patch("os.path.exists", return_value=True),
            ):
                mock_storage_client = Mock()
                mock_bucket = Mock()
                mock_storage_client.bucket.return_value = mock_bucket
                mock_bucket.list_blobs.return_value = []

                with patch(
                    "the_data_packet.generation.audio.storage.Client",
                    return_value=mock_storage_client,
                ):
                    generator = AudioGenerator(gcs_bucket_name="test-bucket")

                    # Test with text that should be split
                    text = "A" * 3000 + "\n" + "B" * 3000
                    chunks = generator.split_text_by_bytes(text, max_bytes=4000)

                    self.assertGreater(len(chunks), 1)
                    for chunk in chunks:
                        self.assertLessEqual(len(chunk.encode("utf-8")), 4000)

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    @patch("time.sleep")
    @patch("tempfile.mktemp")
    @patch("pydub.AudioSegment")
    def test_generate_audio_chunked_success(
        self,
        mock_audio_segment,
        mock_mktemp,
        mock_sleep,
        mock_exists,
        mock_storage,
        mock_tts,
        mock_get_config,
    ):
        """Test successful chunked audio generation."""
        from unittest.mock import MagicMock

        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock TTS long audio client
        mock_tts_client = Mock()
        mock_operation = Mock()
        mock_operation.operation.name = "test-operation"
        mock_operation.done.return_value = True
        mock_operation.result.return_value = Mock()
        mock_tts_client.synthesize_long_audio.return_value = mock_operation
        mock_tts.return_value = mock_tts_client

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        # Mock temp files
        mock_mktemp.side_effect = ["/tmp/chunk1.wav", "/tmp/chunk2.wav"]

        # Mock AudioSegment with proper chaining
        mock_segment = MagicMock()
        mock_segment.duration_seconds = 120.0
        mock_segment.__iadd__ = Mock(return_value=mock_segment)  # For += operator
        mock_segment.__add__ = Mock(return_value=mock_segment)
        mock_segment.export = Mock()
        mock_audio_segment.empty.return_value = mock_segment
        mock_audio_segment.from_wav.return_value = mock_segment

        # Create a long script that will be split
        script = "A" * 3000 + "\nAlex: Part two of the podcast.\n" + "B" * 3000

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        with (
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_path_exists,
            patch("pathlib.Path.unlink"),
        ):
            mock_stat.return_value = Mock(st_size=2048)
            mock_path_exists.return_value = True

            result = generator.generate_audio_chunked(script)

            self.assertIsInstance(result, AudioResult)
            self.assertEqual(result.duration_seconds, 120.0)
            self.assertEqual(result.file_size_bytes, 2048)

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    @patch("pydub.AudioSegment")
    def test_convert_wav_to_mp3(
        self, mock_audio_segment, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test WAV to MP3 conversion."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        # Mock TTS client
        mock_tts.return_value = Mock()

        # Mock AudioSegment
        mock_segment = Mock()
        mock_audio_segment.from_wav.return_value = mock_segment

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        wav_path = Path("/test/input.wav")
        mp3_path = Path("/test/output.mp3")

        generator.convert_wav_to_mp3(wav_path, mp3_path)

        # Verify AudioSegment was called correctly
        mock_audio_segment.from_wav.assert_called_once_with(wav_path)
        mock_segment.export.assert_called_once_with(mp3_path, format="mp3")

    @patch("the_data_packet.generation.audio.get_config")
    @patch(
        "the_data_packet.generation.audio.texttospeech.TextToSpeechLongAudioSynthesizeClient"
    )
    @patch("the_data_packet.generation.audio.storage.Client")
    @patch("os.path.exists")
    def test_generate_audio_calls_chunked_generation(
        self, mock_exists, mock_storage, mock_tts, mock_get_config
    ):
        """Test that generate_audio calls generate_audio_chunked."""
        mock_get_config.return_value = self.mock_config
        mock_exists.return_value = True

        # Mock storage client
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_client

        # Mock TTS client
        mock_tts.return_value = Mock()

        script = """Alex: Hello and welcome to our tech podcast.
Sam: Thanks for having me, Alex. Today we're discussing AI.
Alex: That's right. The latest developments are fascinating.
Sam: Absolutely. Let's dive into the details."""

        generator = AudioGenerator(gcs_bucket_name="test-bucket")

        with patch.object(
            generator,
            "generate_audio_chunked",
            return_value=AudioResult(output_file=Path("test.mp3")),
        ) as mock_chunked:
            result = generator.generate_audio(script)

            # Verify generate_audio_chunked was called
            mock_chunked.assert_called_once()
            self.assertIsInstance(result, AudioResult)


if __name__ == "__main__":
    unittest.main()
