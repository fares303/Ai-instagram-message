"""
Tests for the utils module.
"""

import os
import tempfile
import unittest
from datetime import datetime

from instagram_data_processor import utils


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_fix_broken_text(self):
        """Test the fix_broken_text function."""
        # Test with normal text
        normal_text = "Hello, world!"
        self.assertEqual(utils.fix_broken_text(normal_text), normal_text)

        # Test with broken text
        broken_text = "Ø¶ÙØ§Ù"
        self.assertNotEqual(utils.fix_broken_text(broken_text), broken_text)

        # Test with empty text
        self.assertEqual(utils.fix_broken_text(""), "")

        # Test with None
        self.assertEqual(utils.fix_broken_text(None), "")

    def test_count_emojis(self):
        """Test the count_emojis function."""
        # Test with no emojis
        self.assertEqual(utils.count_emojis("Hello, world!"), 0)

        # Test with emojis
        self.assertEqual(utils.count_emojis("Hello 😊 world! 🌍"), 2)

        # Test with empty text
        self.assertEqual(utils.count_emojis(""), 0)

        # Test with None
        self.assertEqual(utils.count_emojis(None), 0)

    def test_extract_emojis(self):
        """Test the extract_emojis function."""
        # Test with no emojis
        self.assertEqual(utils.extract_emojis("Hello, world!"), [])

        # Test with emojis
        self.assertEqual(utils.extract_emojis("Hello 😊 world! 🌍"), ["😊", "🌍"])

        # Test with empty text
        self.assertEqual(utils.extract_emojis(""), [])

        # Test with None
        self.assertEqual(utils.extract_emojis(None), [])

    def test_contains_phrase(self):
        """Test the contains_phrase function."""
        # Test with matching phrase
        self.assertTrue(utils.contains_phrase("Good morning, world!", ["good morning"]))

        # Test with non-matching phrase
        self.assertFalse(utils.contains_phrase("Hello, world!", ["good morning"]))

        # Test with case sensitivity
        self.assertFalse(utils.contains_phrase("Good morning, world!", ["good morning"], case_sensitive=True))
        self.assertTrue(utils.contains_phrase("Good morning, world!", ["Good morning"], case_sensitive=True))

        # Test with empty text
        self.assertFalse(utils.contains_phrase("", ["good morning"]))

        # Test with None
        self.assertFalse(utils.contains_phrase(None, ["good morning"]))

    def test_setup_directories(self):
        """Test the setup_directories function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test creating directories
            output_dirs = utils.setup_directories(temp_dir)

            # Check that all expected directories were created
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "text")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "pdf")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "excel")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "html")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "media")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "media", "photos")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "media", "videos")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "media", "audio")))

            # Check that the returned dictionary has the correct paths
            self.assertEqual(output_dirs["text"], os.path.join(temp_dir, "text"))
            self.assertEqual(output_dirs["pdf"], os.path.join(temp_dir, "pdf"))
            self.assertEqual(output_dirs["excel"], os.path.join(temp_dir, "excel"))
            self.assertEqual(output_dirs["html"], os.path.join(temp_dir, "html"))
            self.assertEqual(output_dirs["media"], os.path.join(temp_dir, "media"))
            self.assertEqual(output_dirs["photos"], os.path.join(temp_dir, "media", "photos"))
            self.assertEqual(output_dirs["videos"], os.path.join(temp_dir, "media", "videos"))
            self.assertEqual(output_dirs["audio"], os.path.join(temp_dir, "media", "audio"))

    def test_convert_timestamp(self):
        """Test the convert_timestamp function."""
        # Test with a valid timestamp
        timestamp = 1609459200000  # 2021-01-01 00:00:00 UTC
        dt = utils.convert_timestamp(timestamp)
        self.assertIsInstance(dt, datetime)

        # Test with zero
        dt = utils.convert_timestamp(0)
        self.assertIsInstance(dt, datetime)

        # Test with None
        dt = utils.convert_timestamp(None)
        self.assertIsInstance(dt, datetime)

    def test_format_datetime(self):
        """Test the format_datetime function."""
        # Test with a datetime object
        dt = datetime(2021, 1, 1, 12, 0, 0)
        formatted = utils.format_datetime(dt, "%Y-%m-%d")
        self.assertEqual(formatted, "2021-01-01")

        # Test with default format
        formatted = utils.format_datetime(dt)
        self.assertEqual(formatted, "2021-01-01 12:00:00")


if __name__ == "__main__":
    unittest.main()
