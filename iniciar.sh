#!/usr/bin/env bash
set -u

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${APP_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
    zenity --question \
        --title="Instalar Transcriptor MP4" \
        --text="La aplicación necesita una instalación inicial. ¿Abrir el instalador ahora?" \
        --ok-label="Instalar" --cancel-label="Cancelar" || exit 0
    konsole --hold -e bash "${APP_DIR}/instalar.sh"
    exit 0
fi

cd "${APP_DIR}" || exit 1
exec "${PYTHON_BIN}" app.py
