#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
UV_BIN="${HOME}/.local/bin/uv"

if [[ ! -x "${UV_BIN}" ]]; then
    echo "No se encontró uv en ${UV_BIN}."
    echo "Instala uv y vuelve a ejecutar este archivo."
    exit 1
fi

echo "Preparando Transcriptor MP4…"
"${UV_BIN}" venv --python 3.12 "${APP_DIR}/.venv"
"${UV_BIN}" pip install \
    --python "${APP_DIR}/.venv/bin/python" \
    --requirement "${APP_DIR}/requirements.txt"

echo
echo "Instalación terminada. Ya puedes abrir 'Transcriptor MP4' desde el Escritorio."
