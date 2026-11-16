#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APPLICATIONS_DIR="${XDG_DATA_HOME:-${HOME}/.local/share}/applications"

if command -v xdg-user-dir >/dev/null 2>&1; then
    DESKTOP_DIR="$(xdg-user-dir DESKTOP)"
elif [[ -d "${HOME}/Escritorio" ]]; then
    DESKTOP_DIR="${HOME}/Escritorio"
else
    DESKTOP_DIR="${HOME}/Desktop"
fi

write_launcher() {
    local target="$1"
    mkdir -p "$(dirname -- "${target}")"
    {
        printf '%s\n' '[Desktop Entry]'
        printf '%s\n' 'Version=1.0'
        printf '%s\n' 'Type=Application'
        printf '%s\n' 'Name=Transcriptor'
        printf '%s\n' 'Comment=Convierte audios, notas de voz y videos a texto y subtítulos'
        printf 'Exec="%s/iniciar.sh"\n' "${APP_DIR}"
        printf '%s\n' 'Icon=audio-input-microphone'
        printf '%s\n' 'Terminal=false'
        printf '%s\n' 'Categories=AudioVideo;AudioVideoEditing;'
        printf '%s\n' 'StartupNotify=true'
    } > "${target}"
    chmod +x "${target}"
}

write_launcher "${APPLICATIONS_DIR}/transcriptor.desktop"
write_launcher "${DESKTOP_DIR}/Transcriptor.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${APPLICATIONS_DIR}" >/dev/null 2>&1 || true
fi

echo "Acceso directo creado en ${DESKTOP_DIR}/Transcriptor.desktop"
