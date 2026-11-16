import unittest

from transcriptor.ui import human_size


class UiHelpersTests(unittest.TestCase):
    def test_formats_file_sizes_for_the_video_queue(self):
        self.assertEqual(human_size(0), "0 B")
        self.assertEqual(human_size(1_536), "1.5 KB")
        self.assertEqual(human_size(3 * 1024**3), "3.0 GB")


if __name__ == "__main__":
    unittest.main()
