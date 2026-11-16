from pathlib import Path
import tkinter as tk
import unittest

from transcriptor.user_paths import parse_dropped_paths, preferred_user_folder


class UserPathsTests(unittest.TestCase):
    def test_prefers_localized_downloads_folder(self):
        home = Path("/home/persona")
        existing = {home / "Descargas", home / "Downloads"}

        folder = preferred_user_folder(
            "downloads", home=home, is_directory=lambda path: path in existing
        )

        self.assertEqual(folder, home / "Descargas")

    def test_falls_back_to_home_when_known_folder_is_missing(self):
        home = Path("/home/persona")
        folder = preferred_user_folder(
            "videos", home=home, is_directory=lambda _path: False
        )
        self.assertEqual(folder, home)

    def test_parses_dropped_paths_with_spaces_using_tcl_list_rules(self):
        tcl = tk.Tcl()
        dropped = "{/home/persona/Mi video.mp4} /home/persona/otro.mp4"

        self.assertEqual(
            parse_dropped_paths(dropped, tcl.splitlist),
            [
                Path("/home/persona/Mi video.mp4"),
                Path("/home/persona/otro.mp4"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
