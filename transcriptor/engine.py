"""Adaptador perezoso para faster-whisper."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .core import Segment


class TranscriptionCancelled(Exception):
    """Señala una cancelación solicitada por la persona usuaria."""


class WhisperEngine:
    def __init__(self, model_name: str, model: Any | None = None) -> None:
        self.model_name = model_name
        self._model = model

    def _get_model(self) -> Any:
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as error:
                raise RuntimeError(
                    "Falta faster-whisper. Ejecuta instalar.sh y vuelve a abrir la aplicación."
                ) from error
            self._model = WhisperModel(
                self.model_name,
                device="cpu",
                compute_type="int8",
            )
        return self._model

    def transcribe(
        self,
        source: Path,
        language: str | None = None,
        on_progress: Callable[[float], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> tuple[list[Segment], str]:
        cancel_requested = should_cancel or (lambda: False)
        whisper_segments, info = self._get_model().transcribe(
            str(source),
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        duration = max(float(getattr(info, "duration", 0.0)), 0.001)
        result: list[Segment] = []
        for item in whisper_segments:
            if cancel_requested():
                raise TranscriptionCancelled
            result.append(Segment(float(item.start), float(item.end), str(item.text)))
            if on_progress is not None:
                on_progress(min(float(item.end) / duration, 1.0))
        return result, str(getattr(info, "language", language or "desconocido"))
