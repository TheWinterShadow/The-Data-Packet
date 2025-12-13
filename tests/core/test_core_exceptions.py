"""Tests for core exceptions module."""

import unittest

from the_data_packet.core.exceptions import TheDataPacketError


class TestDataPacketError(unittest.TestCase):
    """Test cases for DataPacketError exception."""

    def test_data_packet_error_creation(self):
        """Test DataPacketError can be created and raised."""
        error_message = "Test data packet error"

        with self.assertRaises(DataPacketError) as cm:
            raise DataPacketError(error_message)

        self.assertEqual(str(cm.exception), error_message)

    def test_data_packet_error_inheritance(self):
        """Test DataPacketError inherits from Exception."""
        error = DataPacketError("test")
        self.assertIsInstance(error, Exception)

    def test_data_packet_error_with_cause(self):
        """Test DataPacketError with underlying cause."""
        original_error = ValueError("Original error")

        with self.assertRaises(DataPacketError) as cm:
            try:
                raise original_error
            except ValueError as e:
                raise DataPacketError("Wrapper error") from e

        self.assertEqual(str(cm.exception), "Wrapper error")
        self.assertIsInstance(cm.exception.__cause__, ValueError)


if __name__ == '__main__':
    unittest.main()
