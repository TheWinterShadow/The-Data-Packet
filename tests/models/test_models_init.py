"""Tests for models package __init__.py module."""

import unittest


class TestModelsInit(unittest.TestCase):
    """Test cases for models package __init__.py module."""

    def test_models_module_imports(self):
        """Test that models module classes are importable."""
        from the_data_packet.models import ArticleData

        self.assertIsNotNone(ArticleData)

    def test_models_module_all_exports(self):
        """Test models module __all__ exports."""
        import the_data_packet.models as models_module

        if hasattr(models_module, '__all__'):
            expected_exports = ['ArticleData']
            for export in expected_exports:
                self.assertIn(export, models_module.__all__)


if __name__ == '__main__':
    unittest.main()
