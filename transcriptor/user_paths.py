"""Rutas familiares del usuario y datos recibidos mediante arrastre."""

from collections.abc import Callable, Iterable
from pathlib import Path


FOLDER_NAMES = {
    "downloads": ("Descargas", "Downloads"),
    "videos": ("Vídeos", "Videos"),
    "desktop": ("Escritorio", "Desktop"),
}


def preferred_user_folder(
    kind: str,
    home: Path | None = None,
    is_directory: Callable[[Path], bool] = Path.is_dir,
) -> Path:
    base = home or Path.home()
    for name in FOLDER_NAMES[kind]:
        candidate = base / name
        if is_directory(candidate):
            return candidate
    return base


def parse_dropped_paths(
    data: str,
    split_list: Callable[[str], Iterable[str]],
) -> list[Path]:
    return [Path(item) for item in split_list(data)]
