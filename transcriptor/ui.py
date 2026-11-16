"""Interfaz gráfica del transcriptor local de audio y video."""

from pathlib import Path
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

from .core import save_transcript, validate_media_paths
from .engine import TranscriptionCancelled, WhisperEngine
from .native_dialogs import choose_directory, choose_media_files, kdialog_path
from .theme import apply_theme
from .user_paths import parse_dropped_paths, preferred_user_folder


MODELS = {
    "Rápido · small": "small",
    "Equilibrado · medium": "medium",
    "Máxima precisión · large-v3": "large-v3",
}
MODEL_HELP = {
    "Rápido · small": "Buena precisión y menor consumo. Recomendado para este equipo · ~460 MB",
    "Equilibrado · medium": "Mejor precisión, pero tarda más y necesita más memoria · ~1.5 GB",
    "Máxima precisión · large-v3": "La mejor calidad; puede ser muy lento en CPU · ~3 GB",
}
LANGUAGES = {
    "Detectar automáticamente": None,
    "Español": "es",
    "Inglés": "en",
    "Portugués": "pt",
}


def human_size(byte_count: int) -> str:
    size = float(byte_count)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GB"


class TranscriberApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, style="App.TFrame")
        self.master = master
        self.files: list[Path] = []
        self.file_items: dict[str, Path] = {}
        self.events: queue.Queue[tuple] = queue.Queue()
        self.cancel_event = threading.Event()
        self.running = False
        self.downloads = preferred_user_folder("downloads")
        self.custom_output_folder: Path | None = None
        self.last_result_folder: Path | None = None

        self.model_var = tk.StringVar(value=next(iter(MODELS)))
        self.model_help_var = tk.StringVar(value=MODEL_HELP[self.model_var.get()])
        self.language_var = tk.StringVar(value="Detectar automáticamente")
        self.output_mode_var = tk.StringVar(value="source")
        self.destination_var = tk.StringVar(value="Se guardará junto a cada archivo")
        self.txt_var = tk.BooleanVar(value=True)
        self.srt_var = tk.BooleanVar(value=True)
        self.file_summary_var = tk.StringVar(value="Sin archivos")
        self.status_var = tk.StringVar(value="Listo para comenzar")
        self.progress_text_var = tk.StringVar(value="0%")

        self._build()
        self._poll_events()

    def _build(self) -> None:
        self.grid(sticky="nsew")
        self.master.title("Transcriptor")
        self.master.geometry("900x760")
        self.master.minsize(760, 650)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_media_card()
        self._build_options_card()
        self._build_footer()

    def _build_header(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame", padding=(26, 18))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Transcriptor", style="HeaderTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Convierte audios, notas de voz y videos en texto y subtítulos.",
            style="HeaderSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        ttk.Label(
            header,
            text="● Procesamiento local y privado",
            style="Privacy.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="e")

    def _build_media_card(self) -> None:
        card = ttk.Frame(self, style="Card.TFrame", padding=18)
        card.grid(row=1, column=0, sticky="nsew", padx=22, pady=(18, 10))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        top = ttk.Frame(card, style="Surface.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        top.columnconfigure(0, weight=1)
        ttk.Label(top, text="1  Audios y videos", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(top, textvariable=self.file_summary_var, style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(2, 0)
        )
        self.select_button = ttk.Button(
            top,
            text="Seleccionar archivos…",
            style="Primary.TButton",
            command=self._select_files,
        )
        self.select_button.grid(row=0, column=1, rowspan=2, sticky="e")

        table_frame = ttk.Frame(card, style="Surface.TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.file_table = ttk.Treeview(
            table_frame,
            columns=("name", "folder", "size"),
            show="headings",
            height=7,
            selectmode="extended",
        )
        self.file_table.heading("name", text="Archivo")
        self.file_table.heading("folder", text="Ubicación")
        self.file_table.heading("size", text="Tamaño")
        self.file_table.column("name", width=240, minwidth=140)
        self.file_table.column("folder", width=420, minwidth=220)
        self.file_table.column("size", width=90, minwidth=75, anchor="e")
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.file_table.yview
        )
        self.file_table.configure(yscrollcommand=scrollbar.set)
        self.file_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.empty_label = ttk.Label(
            table_frame,
            text=(
                "Arrastra aquí tus audios o videos\n\n"
                "MP3 · OGG · OPUS · M4A · WAV · MP4"
            ),
            style="Empty.TLabel",
            anchor="center",
            justify="center",
        )
        self.empty_label.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.82)

        for widget in (self.file_table, self.empty_label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<DropEnter>>", self._drop_enter)
            widget.dnd_bind("<<DropLeave>>", self._drop_leave)
            widget.dnd_bind("<<Drop>>", self._drop_files)

        actions = ttk.Frame(card, style="Surface.TFrame")
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        actions.columnconfigure(0, weight=1)
        ttk.Label(
            actions,
            text="Compatible con notas de voz de WhatsApp y varios archivos a la vez.",
            style="Muted.TLabel",
        ).grid(row=0, column=0, sticky="w")
        self.remove_button = ttk.Button(
            actions,
            text="Quitar seleccionados",
            style="Quiet.TButton",
            command=self._remove_selected,
            state="disabled",
        )
        self.remove_button.grid(row=0, column=1)
        self.clear_button = ttk.Button(
            actions,
            text="Vaciar lista",
            style="Quiet.TButton",
            command=self._clear_files,
            state="disabled",
        )
        self.clear_button.grid(row=0, column=2, padx=(6, 0))
        self.file_table.bind("<<TreeviewSelect>>", self._update_remove_button)

    def _build_options_card(self) -> None:
        card = ttk.Frame(self, style="Card.TFrame", padding=18)
        card.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 10))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        ttk.Label(card, text="2  Configuración", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        ttk.Label(card, text="MODELO", style="FieldLabel.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Label(card, text="IDIOMA", style="FieldLabel.TLabel").grid(
            row=1, column=1, sticky="w", padx=(16, 0)
        )
        self.model_combo = ttk.Combobox(
            card, textvariable=self.model_var, values=list(MODELS), state="readonly"
        )
        self.model_combo.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.model_combo.bind("<<ComboboxSelected>>", self._update_model_help)
        self.language_combo = ttk.Combobox(
            card, textvariable=self.language_var, values=list(LANGUAGES), state="readonly"
        )
        self.language_combo.grid(row=2, column=1, sticky="ew", padx=(16, 0), pady=(4, 0))
        ttk.Label(
            card,
            textvariable=self.model_help_var,
            style="Muted.TLabel",
            wraplength=390,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 12))

        ttk.Separator(card).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(card, text="GUARDAR RESULTADOS", style="FieldLabel.TLabel").grid(
            row=5, column=0, columnspan=2, sticky="w"
        )
        output_row = ttk.Frame(card, style="Surface.TFrame")
        output_row.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        output_row.columnconfigure(2, weight=1)
        self.source_radio = ttk.Radiobutton(
            output_row,
            text="Junto a cada archivo",
            variable=self.output_mode_var,
            value="source",
            style="Surface.TRadiobutton",
            command=self._update_output_controls,
        )
        self.source_radio.grid(row=0, column=0, sticky="w")
        self.custom_radio = ttk.Radiobutton(
            output_row,
            text="En otra carpeta",
            variable=self.output_mode_var,
            value="custom",
            style="Surface.TRadiobutton",
            command=self._update_output_controls,
        )
        self.custom_radio.grid(row=0, column=1, sticky="w", padx=(18, 0))
        ttk.Label(
            output_row,
            textvariable=self.destination_var,
            style="Muted.TLabel",
            anchor="e",
        ).grid(row=0, column=2, sticky="ew", padx=(18, 8))
        self.choose_button = ttk.Button(
            output_row,
            text="Elegir carpeta…",
            style="Secondary.TButton",
            command=self._choose_destination,
            state="disabled",
        )
        self.choose_button.grid(row=0, column=3)

        formats = ttk.Frame(card, style="Surface.TFrame")
        formats.grid(row=7, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Label(formats, text="FORMATOS", style="FieldLabel.TLabel").pack(side="left")
        self.txt_check = ttk.Checkbutton(
            formats,
            text="Texto (.txt)",
            variable=self.txt_var,
            style="Surface.TCheckbutton",
        )
        self.txt_check.pack(side="left", padx=(18, 0))
        self.srt_check = ttk.Checkbutton(
            formats,
            text="Subtítulos (.srt)",
            variable=self.srt_var,
            style="Surface.TCheckbutton",
        )
        self.srt_check.pack(side="left", padx=(14, 0))

    def _build_footer(self) -> None:
        footer = ttk.Frame(self, style="App.TFrame", padding=(22, 4, 22, 18))
        footer.grid(row=3, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        ttk.Label(
            footer,
            textvariable=self.status_var,
            foreground="#526469",
            background="#eef2f3",
        ).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 6))
        self.progress = ttk.Progressbar(
            footer, maximum=100, style="Accent.Horizontal.TProgressbar"
        )
        self.progress.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(
            footer,
            textvariable=self.progress_text_var,
            foreground="#526469",
            background="#eef2f3",
            width=4,
            anchor="e",
        ).grid(row=1, column=1, padx=(0, 12))
        self.open_button = ttk.Button(
            footer,
            text="Abrir resultados",
            style="Secondary.TButton",
            command=self._open_results,
            state="disabled",
        )
        self.open_button.grid(row=1, column=2, padx=(0, 8))
        self.start_button = ttk.Button(
            footer,
            text="Transcribir",
            style="Primary.TButton",
            command=self._start,
        )
        self.start_button.grid(row=1, column=3)
        self.cancel_button = ttk.Button(
            footer,
            text="Cancelar",
            style="Secondary.TButton",
            command=self.cancel_event.set,
            state="disabled",
        )
        self.cancel_button.grid(row=1, column=4, padx=(8, 0))

    def _select_files(self) -> None:
        native = kdialog_path()
        if native:
            selected = choose_media_files(self.downloads, kdialog=native)
        else:
            selected = [
                Path(item)
                for item in filedialog.askopenfilenames(
                    title="Seleccionar audios o videos para transcribir",
                    initialdir=str(self.downloads),
                    filetypes=[
                        (
                            "Audio y video",
                            "*.mp4 *.MP4 *.mp3 *.MP3 *.ogg *.OGG *.opus *.OPUS "
                            "*.m4a *.M4A *.wav *.WAV *.aac *.AAC *.flac *.FLAC",
                        )
                    ],
                )
            ]
        self._add_paths(selected)

    def _add_paths(self, paths: list[Path]) -> None:
        valid, invalid = validate_media_paths(paths)
        for path in valid:
            if path not in self.files:
                self.files.append(path)
        self._refresh_file_table()
        if invalid:
            messagebox.showwarning(
                "Archivos omitidos",
                "El archivo no es un audio o video compatible.",
            )

    def _refresh_file_table(self) -> None:
        self.file_table.delete(*self.file_table.get_children())
        self.file_items.clear()
        total_size = 0
        for index, path in enumerate(self.files):
            size = path.stat().st_size
            total_size += size
            item_id = str(index)
            self.file_items[item_id] = path
            self.file_table.insert(
                "",
                "end",
                iid=item_id,
                values=(path.name, str(path.parent), human_size(size)),
            )
        count = len(self.files)
        if count:
            self.file_summary_var.set(f"{count} archivo(s) · {human_size(total_size)} en total")
            self.status_var.set("Archivos listos para transcribir")
            self.empty_label.place_forget()
            self.clear_button.configure(state="normal" if not self.running else "disabled")
        else:
            self.file_summary_var.set("Sin archivos")
            self.status_var.set("Selecciona o arrastra audios y videos")
            self.empty_label.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.82)
            self.clear_button.configure(state="disabled")
        self._update_remove_button()

    def _drop_enter(self, event):
        if not self.running:
            self.empty_label.configure(style="Drop.Empty.TLabel")
        return event.action

    def _drop_leave(self, event):
        self.empty_label.configure(style="Empty.TLabel")
        return event.action

    def _drop_files(self, event):
        self.empty_label.configure(style="Empty.TLabel")
        if not self.running:
            self._add_paths(parse_dropped_paths(event.data, self.master.tk.splitlist))
        return event.action

    def _remove_selected(self) -> None:
        selected = [self.file_items[item] for item in self.file_table.selection()]
        self.files = [path for path in self.files if path not in selected]
        self._refresh_file_table()

    def _clear_files(self) -> None:
        self.files.clear()
        self._refresh_file_table()

    def _update_remove_button(self, _event=None) -> None:
        enabled = bool(self.file_table.selection()) and not self.running
        self.remove_button.configure(state="normal" if enabled else "disabled")

    def _update_model_help(self, _event=None) -> None:
        self.model_help_var.set(MODEL_HELP[self.model_var.get()])

    def _update_output_controls(self) -> None:
        custom = self.output_mode_var.get() == "custom" and not self.running
        self.choose_button.configure(state="normal" if custom else "disabled")
        if self.output_mode_var.get() == "source":
            self.destination_var.set("Se guardará junto a cada archivo")
        elif self.custom_output_folder is None:
            self.destination_var.set("Selecciona una carpeta")
        else:
            self.destination_var.set(str(self.custom_output_folder))

    def _choose_destination(self) -> None:
        initial = self.custom_output_folder or Path.home()
        native = kdialog_path()
        if native:
            folder = choose_directory(initial, kdialog=native)
        else:
            selected = filedialog.askdirectory(
                title="Elegir carpeta para las transcripciones",
                initialdir=str(initial),
            )
            folder = Path(selected) if selected else None
        if folder:
            self.output_mode_var.set("custom")
            self.custom_output_folder = folder
            self.destination_var.set(str(folder))
            self._update_output_controls()

    def _start(self) -> None:
        if not self.files:
            messagebox.showinfo("Faltan archivos", "Selecciona al menos un audio o video.")
            return
        if not self.txt_var.get() and not self.srt_var.get():
            messagebox.showinfo("Falta formato", "Marca Texto, Subtítulos o ambos.")
            return
        custom_output = self.output_mode_var.get() == "custom"
        if custom_output and self.custom_output_folder is None:
            messagebox.showinfo(
                "Falta la carpeta",
                "Elige la carpeta donde quieres guardar los resultados.",
            )
            self._choose_destination()
            return

        destination = self.custom_output_folder if custom_output else None
        self.last_result_folder = destination or self.files[0].parent
        self.running = True
        self.cancel_event.clear()
        self.progress["value"] = 0
        self.progress_text_var.set("0%")
        self.status_var.set("Preparando el modelo… La primera vez puede tardar.")
        self.open_button.configure(state="disabled")
        self._set_controls(False)
        threading.Thread(
            target=self._run_batch,
            args=(
                tuple(self.files),
                MODELS[self.model_var.get()],
                LANGUAGES[self.language_var.get()],
                destination,
                (self.txt_var.get(), self.srt_var.get()),
            ),
            daemon=True,
        ).start()

    def _run_batch(
        self,
        files: tuple[Path, ...],
        model_name: str,
        language: str | None,
        destination: Path | None,
        formats: tuple[bool, bool],
    ) -> None:
        try:
            engine = WhisperEngine(model_name)
            total = len(files)
            for index, source in enumerate(files):
                if self.cancel_event.is_set():
                    raise TranscriptionCancelled
                self.events.put(
                    ("status", f"Transcribiendo {source.name} · {index + 1} de {total}")
                )
                segments, detected = engine.transcribe(
                    source,
                    language=language,
                    should_cancel=self.cancel_event.is_set,
                    on_progress=lambda value, i=index: self.events.put(
                        ("progress", 100 * (i + value) / total)
                    ),
                )
                created = save_transcript(
                    source,
                    segments,
                    destination,
                    write_txt=formats[0],
                    write_srt=formats[1],
                )
                self.events.put(
                    (
                        "status",
                        f"Guardado {', '.join(path.name for path in created)} · idioma {detected}",
                    )
                )
            self.events.put(("done", f"{total} archivo(s) transcrito(s) correctamente."))
        except TranscriptionCancelled:
            self.events.put(("cancelled", "Transcripción cancelada."))
        except Exception as error:
            self.events.put(("error", str(error)))

    def _poll_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "progress":
                    self.progress["value"] = value
                    self.progress_text_var.set(f"{value:.0f}%")
                elif kind == "status":
                    self.status_var.set(value)
                elif kind in {"done", "cancelled", "error"}:
                    self.running = False
                    self._set_controls(True)
                    self.status_var.set(value)
                    if kind == "done":
                        self.progress["value"] = 100
                        self.progress_text_var.set("100%")
                        self.open_button.configure(state="normal")
                        messagebox.showinfo("Transcripción terminada", value)
                    elif kind == "error":
                        messagebox.showerror("No se pudo transcribir", value)
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def _open_results(self) -> None:
        if self.last_result_folder is None:
            return
        try:
            subprocess.Popen(
                ["xdg-open", str(self.last_result_folder)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as error:
            messagebox.showerror("No se pudo abrir la carpeta", str(error))

    def _set_controls(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for widget in (
            self.select_button,
            self.clear_button,
            self.start_button,
            self.source_radio,
            self.custom_radio,
            self.txt_check,
            self.srt_check,
        ):
            widget.configure(state=state)
        self.model_combo.configure(state="readonly" if enabled else "disabled")
        self.language_combo.configure(state="readonly" if enabled else "disabled")
        self.cancel_button.configure(state="disabled" if enabled else "normal")
        self._update_output_controls()
        self._update_remove_button()
        if enabled and not self.files:
            self.clear_button.configure(state="disabled")


def run() -> None:
    root = TkinterDnD.Tk()
    apply_theme(root)
    app = TranscriberApp(root)

    def close() -> None:
        if app.running and not messagebox.askyesno(
            "Salir", "Hay una transcripción en curso. ¿Quieres cancelarla y salir?"
        ):
            return
        app.cancel_event.set()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()
