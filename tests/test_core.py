from pathlib import Path
import tempfile
import unittest

from transcriptor.core import (
    Segment,
    build_srt,
    build_text,
    format_srt_timestamp,
    output_paths,
    validate_media_paths,
)


class CoreTests(unittest.TestCase):
    def test_formats_srt_timestamp_with_milliseconds(self):
        self.assertEqual(format_srt_timestamp(3661.2346), "01:01:01,235")

    def test_builds_clean_plain_text(self):
        segments = [
            Segment(0.0, 1.5, "  Hola mundo. "),
            Segment(1.5, 3.0, "Esta es una prueba.  "),
        ]
        self.assertEqual(build_text(segments), "Hola mundo.\nEsta es una prueba.\n")

    def test_builds_numbered_srt(self):
        segments = [
            Segment(0.0, 1.5, " Hola mundo. "),
            Segment(1.5, 3.0, "Segunda línea."),
        ]
        self.assertEqual(
            build_srt(segments),
            "1\n00:00:00,000 --> 00:00:01,500\nHola mundo.\n\n"
            "2\n00:00:01,500 --> 00:00:03,000\nSegunda línea.\n",
        )

    def test_srt_numbers_remain_consecutive_when_a_segment_is_empty(self):
        segments = [
            Segment(0.0, 1.0, "Primero"),
            Segment(1.0, 2.0, "   "),
            Segment(2.0, 3.0, "Segundo"),
        ]

        self.assertEqual(
            build_srt(segments),
            "1\n00:00:00,000 --> 00:00:01,000\nPrimero\n\n"
            "2\n00:00:02,000 --> 00:00:03,000\nSegundo\n",
        )

    def test_output_paths_can_use_source_or_custom_directory(self):
        source = Path("/videos/clase.mp4")
        self.assertEqual(
            output_paths(source),
            (Path("/videos/clase.txt"), Path("/videos/clase.srt")),
        )
        self.assertEqual(
            output_paths(source, Path("/salida")),
            (Path("/salida/clase.txt"), Path("/salida/clase.srt")),
        )

    def test_validation_accepts_existing_media_and_rejects_other_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            video = folder / "clase.MP4"
            text = folder / "notas.txt"
            video.touch()
            text.touch()

            valid, invalid = validate_media_paths([video, text, folder / "falta.mp4"])

            self.assertEqual(valid, [video])
            self.assertEqual(invalid, [text, folder / "falta.mp4"])

    def test_media_validation_accepts_whatsapp_and_common_audio_formats(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            supported = [
                folder / "nota.mp3",
                folder / "voz-whatsapp.ogg",
                folder / "voz-whatsapp.opus",
                folder / "grabacion.m4a",
                folder / "entrevista.wav",
                folder / "audio.aac",
                folder / "archivo.flac",
            ]
            unsupported = folder / "documento.pdf"
            for path in [*supported, unsupported]:
                path.touch()

            valid, invalid = validate_media_paths([*supported, unsupported])

            self.assertEqual(valid, supported)
            self.assertEqual(invalid, [unsupported])


if __name__ == "__main__":
    unittest.main()
