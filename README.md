# Transcriptor

Aplicación local para convertir audios, notas de voz y videos en:

- texto plano (`.txt`);
- subtítulos con tiempos (`.srt`).

Los archivos no se suben a internet. La aplicación usa `faster-whisper` en el
equipo y guarda los resultados junto al original o en la carpeta que elijas.

Formatos compatibles: MP4, MP3, OGG, OPUS (notas de voz de WhatsApp), M4A,
WAV, AAC y FLAC.

## Uso

1. Abre **Transcriptor** desde el Escritorio.
2. Arrastra uno o varios audios o videos sobre la zona de archivos, o pulsa
   **Seleccionar archivos** para usar el explorador nativo de KDE.
3. Elige modelo, idioma y formatos de salida.
4. Decide si los resultados se guardan junto a cada archivo o en otra carpeta.
5. Pulsa **Transcribir**. Al terminar puedes abrir directamente la carpeta de
   resultados.

La primera transcripción descarga el modelo seleccionado. El modelo rápido
ocupa aproximadamente 460 MB; los modelos más precisos necesitan más espacio,
memoria y tiempo. En equipos sin GPU, un archivo puede tardar tanto como su
duración o más.

## Reinstalación

Ejecuta `instalar.sh` desde una terminal. La aplicación requiere conexión solo
para instalar las dependencias y descargar por primera vez cada modelo.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```
