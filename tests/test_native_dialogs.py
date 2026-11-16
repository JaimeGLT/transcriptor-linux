from pathlib import Path
from types import SimpleNamespace
import unittest

from transcriptor.native_dialogs import choose_directory, choose_video_files


class NativeDialogsTests(unittest.TestCase):
    def test_video_picker_uses_kde_native_multiple_file_dialog(self):
        calls: list[list[str]] = []

        def run(command, **_options):
            calls.append(command)
            return SimpleNamespace(
                returncode=0,
                stdout="/home/persona/Descargas/uno.mp4\n"
                "/home/persona/Descargas/dos.MP4\n",
            )

        selected = choose_video_files(
            Path("/home/persona/Descargas"),
            kdialog="/usr/bin/kdialog",
            runner=run,
        )

        self.assertEqual(
            selected,
            [
                Path("/home/persona/Descargas/uno.mp4"),
                Path("/home/persona/Descargas/dos.MP4"),
            ],
        )
        self.assertIn("--multiple", calls[0])
        self.assertIn("--separate-output", calls[0])
        self.assertIn("--getopenfilename", calls[0])

    def test_video_picker_returns_empty_selection_when_cancelled(self):
        def run(_command, **_options):
            return SimpleNamespace(returncode=1, stdout="")

        self.assertEqual(
            choose_video_files(Path.home(), kdialog="kdialog", runner=run),
            [],
        )

    def test_directory_picker_returns_selected_native_folder(self):
        def run(command, **_options):
            self.assertIn("--getexistingdirectory", command)
            return SimpleNamespace(returncode=0, stdout="/home/persona/Documentos\n")

        self.assertEqual(
            choose_directory(Path.home(), kdialog="kdialog", runner=run),
            Path("/home/persona/Documentos"),
        )


if __name__ == "__main__":
    unittest.main()
