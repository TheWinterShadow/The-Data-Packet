"""Tests for workflows package __init__.py module."""

import unittest


class TestWorkflowsInit(unittest.TestCase):
    """Test cases for workflows package __init__.py module."""

    def test_workflows_module_imports(self):
        """Test that workflows module classes are importable."""
        from the_data_packet.workflows import PipelineConfig, PodcastPipeline

        self.assertIsNotNone(PipelineConfig)
        self.assertIsNotNone(PodcastPipeline)

    def test_workflows_module_all_exports(self):
        """Test workflows module __all__ exports."""
        import the_data_packet.workflows as workflows_module

        if hasattr(workflows_module, '__all__'):
            expected_exports = ['PipelineConfig', 'PodcastPipeline']
            for export in expected_exports:
                self.assertIn(export, workflows_module.__all__)


if __name__ == '__main__':
    unittest.main()
