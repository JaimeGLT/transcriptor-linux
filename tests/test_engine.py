from pathlib import Path
from types import SimpleNamespace
import unittest

from transcriptor.engine import TranscriptionCancelled, WhisperEngine


class FakeModel:
    def transcribe(self, _path, **_options):
        segments = [
            SimpleNamespace(start=0.0, end=2.0, text=" Hola"),
            SimpleNamespace(start=2.0, end=5.0, text=" mundo"),
        ]
        return iter(segments), SimpleNamespace(duration=5.0, language="es")


class EngineTests(unittest.TestCase):
    def test_converts_whisper_segments_and_reports_progress(self):
        progress: list[float] = []
        engine = WhisperEngine("small", model=FakeModel())

        segments, language = engine.transcribe(
            Path("clase.mp4"),
            language=None,
            on_progress=progress.append,
        )

        self.assertEqual([segment.text for segment in segments], [" Hola", " mundo"])
        self.assertEqual(language, "es")
        self.assertEqual(progress, [0.4, 1.0])

    def test_stops_between_segments_when_cancelled(self):
        calls = 0

        def should_cancel():
            nonlocal calls
            calls += 1
            return calls > 1

        engine = WhisperEngine("small", model=FakeModel())

        with self.assertRaises(TranscriptionCancelled):
            engine.transcribe(Path("clase.mp4"), should_cancel=should_cancel)


if __name__ == "__main__":
    unittest.main()
