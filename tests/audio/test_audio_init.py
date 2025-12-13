"""Tests for audio package __init__.py module."""

import unittest


class TestAudioInit(unittest.TestCase):
    """Test cases for audio package __init__.py module."""

    def test_audio_module_imports(self):
        """Test that audio module classes are importable."""
        from the_data_packet.audio import GeminiTTSGenerator

        self.assertIsNotNone(GeminiTTSGenerator)

    def test_audio_module_all_exports(self):
        """Test audio module __all__ exports."""
        import the_data_packet.audio as audio_module

        if hasattr(audio_module, '__all__'):
            expected_exports = ['GeminiTTSGenerator']
            for export in expected_exports:
                self.assertIn(export, audio_module.__all__)


if __name__ == '__main__':
    unittest.main()
