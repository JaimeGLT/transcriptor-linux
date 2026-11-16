# Transcriptor

Aplicación de escritorio para Linux que convierte audios, notas de voz y
videos en texto plano (`.txt`) y subtítulos (`.srt`). El procesamiento se hace
localmente con `faster-whisper`: los archivos no se suben a un servicio externo
y no se necesita una clave de API.

## Funciones

- Transcripción por lotes de uno o varios archivos.
- Arrastrar y soltar desde el explorador de archivos.
- Selector nativo de KDE mediante `kdialog`, con alternativa de Tk.
- Detección automática de idioma o selección manual de español, inglés y
  portugués.
- Modelos `small`, `medium` y `large-v3`.
- Resultados junto al archivo original o en una carpeta personalizada.
- Progreso, cancelación y acceso directo a la carpeta de resultados.

Formatos aceptados:

| Tipo | Extensiones |
| --- | --- |
| Video | `.mp4` |
| Audio | `.mp3`, `.m4a`, `.wav`, `.aac`, `.flac` |
| Notas de voz de WhatsApp | `.ogg`, `.opus` |

## Requisitos

- Linux de 64 bits.
- Entorno gráfico con Tk. KDE Plasma es recomendado, pero no obligatorio.
- `uv` para instalar Python 3.12 y las dependencias en un entorno aislado.
- Conexión a internet durante la instalación y la primera descarga de cada
  modelo Whisper.
- Aproximadamente 2 GB libres para el entorno y el modelo `small`.
- 4 GB de RAM como mínimo; 8 GB o más es recomendable.

No es necesario instalar FFmpeg: PyAV incluye las bibliotecas necesarias para
decodificar los formatos compatibles.

## Instalación rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/JaimeGLT/transcriptor-linux.git
cd transcriptor-linux
```

### 2. Instalar `uv`

Si todavía no está instalado, usa el instalador oficial:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Cierra y abre la terminal después de instalarlo, o carga nuevamente la
configuración de tu shell.

### 3. Instalar la aplicación

```bash
chmod +x instalar.sh iniciar.sh crear-acceso-directo.sh
./instalar.sh
```

El instalador:

1. descarga Python 3.12 mediante `uv` si es necesario;
2. crea `.venv` dentro del proyecto;
3. instala las versiones compatibles de `faster-whisper`, PyAV y
   `tkinterdnd2`;
4. crea un acceso en el Escritorio y otro en el menú de aplicaciones.

## Ejecutar desde una terminal

```bash
./iniciar.sh
```

También se puede ejecutar directamente:

```bash
.venv/bin/python app.py
```

## Crear o reparar los accesos directos

```bash
./crear-acceso-directo.sh
```

El script detecta la carpeta Escritorio mediante `xdg-user-dir` y crea:

- `Transcriptor.desktop` en el Escritorio;
- `transcriptor.desktop` en `~/.local/share/applications`, para que aparezca
  en el menú del sistema.

Los accesos utilizan la ruta real del repositorio, por lo que funcionan aunque
el proyecto se clone en una ubicación diferente.

## Uso

1. Abre **Transcriptor**.
2. Arrastra archivos sobre la ventana o pulsa **Seleccionar archivos**.
3. Elige modelo, idioma y formatos de salida.
4. Decide si los resultados se guardan junto al original o en otra carpeta.
5. Pulsa **Transcribir**.

La primera ejecución de un modelo lo descarga. Los tamaños aproximados son:

| Modelo | Descarga | Uso recomendado |
| --- | ---: | --- |
| `small` | 460 MB | Uso general y equipos modestos |
| `medium` | 1.5 GB | Mejor precisión, mayor consumo |
| `large-v3` | 3 GB | Máxima precisión y equipos potentes |

## Ejecutar las pruebas

Después de la instalación:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

La suite cubre generación de TXT/SRT, formatos multimedia, notas de voz,
cancelación, diálogos nativos y compatibilidad entre `faster-whisper` y PyAV.

## Estructura del proyecto

```text
app.py                         Entrada de la aplicación
transcriptor/ui.py             Ventana y flujo de interacción
transcriptor/theme.py          Tema visual
transcriptor/engine.py         Adaptador de faster-whisper
transcriptor/core.py           Validación y generación de TXT/SRT
transcriptor/native_dialogs.py Integración con el selector de KDE
tests/                         Pruebas automatizadas
instalar.sh                    Instalación reproducible
iniciar.sh                     Lanzador local
crear-acceso-directo.sh        Accesos del Escritorio y menú
```

## Empaquetado Linux

Actualmente el proyecto se distribuye como código fuente con un instalador.
No genera todavía paquetes `.deb`, RPM o AppImage. Para distribuir una versión
portable habría que incorporar un proceso de empaquetado que incluya Python,
Tk/TkDnD y las bibliotecas nativas de CTranslate2 y PyAV; copiar solamente
`app.py` no es suficiente.

## ¿Se puede generar un APK?

No directamente. Un APK es una aplicación Android, mientras que este proyecto
usa Tkinter, TkDnD y herramientas de escritorio Linux. Una versión Android
necesitaría otra interfaz (por ejemplo, Kotlin, Flutter o Kivy) y empaquetar un
motor Whisper compatible con Android. El código de transcripción y generación
de resultados puede servir como referencia, pero este repositorio no produce
un APK.

## Solución de problemas

### El modelo tarda en iniciar

La primera ejecución descarga el modelo seleccionado. Después queda almacenado
en la caché local.

### El selector no parece nativo

En KDE, instala `kdialog`. Si no está disponible, la aplicación usa el selector
incluido en Tkinter.

### La transcripción consume mucha memoria

Usa el modelo `small` y cierra aplicaciones pesadas. Los modelos `medium` y
`large-v3` requieren bastante más memoria.

### Error relacionado con `metadata_errors`

Ejecuta nuevamente `./instalar.sh`. El proyecto fija PyAV 18.1.0 porque es la
versión compatible con `faster-whisper` 1.2.1.

## Privacidad

La inferencia se ejecuta localmente. Solo hay conexiones externas durante la
instalación de dependencias y la descarga inicial de los modelos.
