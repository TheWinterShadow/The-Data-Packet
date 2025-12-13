"""Tests for ai package __init__.py module."""

import unittest


class TestAIInit(unittest.TestCase):
    """Test cases for ai package __init__.py module."""

    def test_ai_module_imports(self):
        """Test that AI module classes are importable."""
        from the_data_packet.ai import ClaudeClient, ScriptGenerator

        self.assertIsNotNone(ClaudeClient)
        self.assertIsNotNone(ScriptGenerator)

    def test_ai_module_all_exports(self):
        """Test AI module __all__ exports."""
        import the_data_packet.ai as ai_module

        if hasattr(ai_module, '__all__'):
            expected_exports = ['ClaudeClient', 'ScriptGenerator']
            for export in expected_exports:
                self.assertIn(export, ai_module.__all__)


if __name__ == '__main__':
    unittest.main()
