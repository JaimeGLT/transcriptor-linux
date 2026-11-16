# Transcriptor MP4

Aplicación local para convertir uno o varios videos MP4 en:

- texto plano (`.txt`);
- subtítulos con tiempos (`.srt`).

Los videos no se suben a internet. La aplicación usa `faster-whisper` en el
equipo y guarda los resultados junto al video o en la carpeta que elijas.

## Uso

1. Abre **Transcriptor MP4** desde el Escritorio.
2. Arrastra uno o varios MP4 sobre la zona de videos, o pulsa
   **Seleccionar videos** para usar el explorador nativo de KDE.
3. Elige modelo, idioma y formatos de salida.
4. Decide si los resultados se guardan junto a cada video o en otra carpeta.
5. Pulsa **Transcribir**. Al terminar puedes abrir directamente la carpeta de
   resultados.

La primera transcripción descarga el modelo seleccionado. El modelo rápido
ocupa aproximadamente 460 MB; los modelos más precisos necesitan más espacio,
memoria y tiempo. En equipos sin GPU, un video puede tardar tanto como su
duración o más.

## Reinstalación

Ejecuta `instalar.sh` desde una terminal. La aplicación requiere conexión solo
para instalar las dependencias y descargar por primera vez cada modelo.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```
