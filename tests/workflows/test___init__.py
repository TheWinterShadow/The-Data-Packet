"""Unit tests for workflows.__init__.py module."""

import unittest

from the_data_packet.workflows import PodcastPipeline, PodcastResult


class TestWorkflowsInit(unittest.TestCase):
    """Test cases for workflows module initialization."""

    def test_all_imports_available(self):
        """Test that all expected workflows are importable."""
        # Test that classes exist and are importable
        self.assertIsNotNone(PodcastPipeline)
        self.assertIsNotNone(PodcastResult)

    def test_classes_are_callable(self):
        """Test that imported workflows are actually classes."""
        self.assertTrue(callable(PodcastPipeline))
        self.assertTrue(callable(PodcastResult))

    def test_module_all_attribute(self):
        """Test that __all__ attribute contains expected items."""
        import the_data_packet.workflows as workflows_module

        expected_items = ["PodcastPipeline", "PodcastResult"]

        self.assertTrue(hasattr(workflows_module, "__all__"))
        for item in expected_items:
            self.assertIn(item, workflows_module.__all__)

    def test_import_structure(self):
        """Test that workflows come from expected modules."""
        # Test that we can access the workflows as expected
        from the_data_packet.workflows.podcast import (
            PodcastPipeline as PodcastPipelineDirect,
        )
        from the_data_packet.workflows.podcast import (
            PodcastResult as PodcastResultDirect,
        )

        # Should be the same classes
        self.assertIs(PodcastPipeline, PodcastPipelineDirect)
        self.assertIs(PodcastResult, PodcastResultDirect)


if __name__ == "__main__":
    unittest.main()
