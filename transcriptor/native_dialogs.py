"""Selectores de archivos nativos de KDE con una interfaz pequeña y comprobable."""

from collections.abc import Callable
from pathlib import Path
import shutil
import subprocess
from typing import Any


Runner = Callable[..., Any]
MEDIA_NAME_FILTER = (
    "Audio y video (*.mp4 *.MP4 *.mp3 *.MP3 *.ogg *.OGG *.opus *.OPUS "
    "*.m4a *.M4A *.wav *.WAV *.aac *.AAC *.flac *.FLAC)"
)


def kdialog_path() -> str | None:
    return shutil.which("kdialog")


def choose_media_files(
    initial_directory: Path,
    *,
    kdialog: str,
    runner: Runner = subprocess.run,
) -> list[Path]:
    result = runner(
        [
            kdialog,
            "--title",
            "Seleccionar audios o videos para transcribir",
            "--getopenfilename",
            str(initial_directory),
            MEDIA_NAME_FILTER,
            "--multiple",
            "--separate-output",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def choose_directory(
    initial_directory: Path,
    *,
    kdialog: str,
    runner: Runner = subprocess.run,
) -> Path | None:
    result = runner(
        [
            kdialog,
            "--title",
            "Elegir carpeta para las transcripciones",
            "--getexistingdirectory",
            str(initial_directory),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip())
