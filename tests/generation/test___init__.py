"""Unit tests for generation.__init__.py module."""

import unittest

from the_data_packet.generation import AudioGenerator, RSSGenerator, ScriptGenerator


class TestGenerationInit(unittest.TestCase):
    """Test cases for generation module initialization."""

    def test_all_imports_available(self):
        """Test that all expected generators are importable."""
        # Test that classes exist and are importable
        self.assertIsNotNone(ScriptGenerator)
        self.assertIsNotNone(AudioGenerator)
        self.assertIsNotNone(RSSGenerator)

    def test_generator_classes_are_classes(self):
        """Test that imported generators are actually classes."""
        self.assertTrue(callable(ScriptGenerator))
        self.assertTrue(callable(AudioGenerator))
        self.assertTrue(callable(RSSGenerator))

    def test_module_all_attribute(self):
        """Test that __all__ attribute contains expected items."""
        import the_data_packet.generation as gen_module

        expected_items = ["ScriptGenerator", "AudioGenerator", "RSSGenerator"]

        self.assertTrue(hasattr(gen_module, "__all__"))
        for item in expected_items:
            self.assertIn(item, gen_module.__all__)


if __name__ == "__main__":
    unittest.main()
