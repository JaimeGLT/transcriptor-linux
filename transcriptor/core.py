"""Lógica independiente de la interfaz para preparar transcripciones."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


def format_srt_timestamp(seconds: float) -> str:
    total_milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def build_text(segments: Iterable[Segment]) -> str:
    lines = [segment.text.strip() for segment in segments if segment.text.strip()]
    return "\n".join(lines) + ("\n" if lines else "")


def build_srt(segments: Iterable[Segment]) -> str:
    blocks: list[str] = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        index = len(blocks) + 1
        blocks.append(
            f"{index}\n"
            f"{format_srt_timestamp(segment.start)} --> "
            f"{format_srt_timestamp(segment.end)}\n"
            f"{text}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def output_paths(source: Path, destination: Path | None = None) -> tuple[Path, Path]:
    folder = destination if destination is not None else source.parent
    return folder / f"{source.stem}.txt", folder / f"{source.stem}.srt"


def validate_video_paths(paths: Iterable[Path]) -> tuple[list[Path], list[Path]]:
    valid: list[Path] = []
    invalid: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".mp4":
            valid.append(path)
        else:
            invalid.append(path)
    return valid, invalid


def save_transcript(
    source: Path,
    segments: Iterable[Segment],
    destination: Path | None = None,
    write_txt: bool = True,
    write_srt: bool = True,
) -> list[Path]:
    materialized = list(segments)
    txt_path, srt_path = output_paths(source, destination)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    if write_txt:
        txt_path.write_text(build_text(materialized), encoding="utf-8")
        created.append(txt_path)
    if write_srt:
        srt_path.write_text(build_srt(materialized), encoding="utf-8")
        created.append(srt_path)
    return created
