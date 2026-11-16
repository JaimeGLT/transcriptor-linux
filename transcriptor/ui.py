"""Interfaz gráfica de Transcriptor MP4."""

from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

from .core import save_transcript, validate_video_paths
from .engine import TranscriptionCancelled, WhisperEngine
from .user_paths import parse_dropped_paths, preferred_user_folder


MODELS = {
    "Rápido — small (~460 MB)": "small",
    "Más preciso — medium (~1.5 GB)": "medium",
    "Máxima precisión — large-v3 (~3 GB)": "large-v3",
}
LANGUAGES = {
    "Detectar automáticamente": None,
    "Español": "es",
    "Inglés": "en",
    "Portugués": "pt",
}


class TranscriberApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=20)
        self.master = master
        self.files: list[Path] = []
        self.events: queue.Queue[tuple] = queue.Queue()
        self.cancel_event = threading.Event()
        self.running = False
        self.quick_folders = {
            "Descargas": preferred_user_folder("downloads"),
            "Videos": preferred_user_folder("videos"),
            "Escritorio": preferred_user_folder("desktop"),
        }
        self.folder_buttons: list[ttk.Button] = []

        self.model_var = tk.StringVar(value=next(iter(MODELS)))
        self.language_var = tk.StringVar(value="Detectar automáticamente")
        self.destination_var = tk.StringVar()
        self.txt_var = tk.BooleanVar(value=True)
        self.srt_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Agrega uno o varios videos MP4 para comenzar.")
        self._build()
        self._poll_events()

    def _build(self) -> None:
        self.grid(sticky="nsew")
        self.master.title("Transcriptor MP4")
        self.master.geometry("760x650")
        self.master.minsize(620, 540)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="Transcriptor MP4", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            self,
            text="Convierte videos a texto y subtítulos sin subirlos a internet.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 16))

        files_box = ttk.LabelFrame(self, text="1. Videos", padding=12)
        files_box.grid(row=2, column=0, sticky="nsew")
        files_box.columnconfigure(0, weight=1)
        files_box.rowconfigure(2, weight=1)
        quick_bar = ttk.Frame(files_box)
        quick_bar.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(quick_bar, text="Buscar en:").pack(side="left", padx=(0, 6))
        for label, folder in self.quick_folders.items():
            button = ttk.Button(
                quick_bar,
                text=label,
                command=lambda path=folder: self._add_files(path),
            )
            button.pack(side="left", padx=(0, 6))
            self.folder_buttons.append(button)
        self.add_button = ttk.Button(
            quick_bar, text="Otra carpeta…", command=self._add_files
        )
        self.add_button.pack(side="left")
        ttk.Label(
            files_box,
            text="También puedes arrastrar y soltar aquí uno o varios videos MP4 ↓",
            style="DropHint.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.file_list = tk.Listbox(
            files_box,
            selectmode=tk.EXTENDED,
            activestyle="dotbox",
            height=8,
            background="#f8fafc",
            highlightthickness=2,
            highlightbackground="#94a3b8",
            highlightcolor="#2563eb",
        )
        scrollbar = ttk.Scrollbar(files_box, orient="vertical", command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scrollbar.set)
        self.file_list.grid(row=2, column=0, sticky="nsew")
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.file_list.drop_target_register(DND_FILES)
        self.file_list.dnd_bind("<<DropEnter>>", self._drop_enter)
        self.file_list.dnd_bind("<<DropLeave>>", self._drop_leave)
        self.file_list.dnd_bind("<<Drop>>", self._drop_files)
        button_bar = ttk.Frame(files_box)
        button_bar.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.remove_button = ttk.Button(
            button_bar, text="Quitar seleccionados", command=self._remove_selected
        )
        self.remove_button.pack(side="left")

        options = ttk.LabelFrame(self, text="2. Opciones", padding=12)
        options.grid(row=3, column=0, sticky="ew", pady=12)
        options.columnconfigure(1, weight=1)
        ttk.Label(options, text="Modelo:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.model_combo = ttk.Combobox(
            options, textvariable=self.model_var, values=list(MODELS), state="readonly"
        )
        self.model_combo.grid(row=0, column=1, sticky="ew")
        ttk.Label(options, text="Idioma:").grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0)
        )
        self.language_combo = ttk.Combobox(
            options, textvariable=self.language_var, values=list(LANGUAGES), state="readonly"
        )
        self.language_combo.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        ttk.Label(options, text="Salida:").grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0)
        )
        destination_row = ttk.Frame(options)
        destination_row.grid(row=2, column=1, sticky="ew", pady=(8, 0))
        destination_row.columnconfigure(0, weight=1)
        self.destination_entry = ttk.Entry(
            destination_row,
            textvariable=self.destination_var,
            state="readonly",
        )
        self.destination_entry.grid(row=0, column=0, sticky="ew")
        self.choose_button = ttk.Button(
            destination_row, text="Elegir…", command=self._choose_destination
        )
        self.choose_button.grid(row=0, column=1, padx=(8, 0))
        ttk.Label(
            options,
            text="Vacío = guardar junto a cada video",
            style="Hint.TLabel",
        ).grid(row=3, column=1, sticky="w", pady=(2, 0))
        formats = ttk.Frame(options)
        formats.grid(row=4, column=1, sticky="w", pady=(8, 0))
        ttk.Checkbutton(formats, text="Texto (.txt)", variable=self.txt_var).pack(side="left")
        ttk.Checkbutton(formats, text="Subtítulos (.srt)", variable=self.srt_var).pack(
            side="left", padx=(16, 0)
        )

        action_bar = ttk.Frame(self)
        action_bar.grid(row=4, column=0, sticky="ew")
        action_bar.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(action_bar, maximum=100)
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.start_button = ttk.Button(
            action_bar, text="Transcribir", style="Accent.TButton", command=self._start
        )
        self.start_button.grid(row=0, column=1)
        self.cancel_button = ttk.Button(
            action_bar, text="Cancelar", command=self.cancel_event.set, state="disabled"
        )
        self.cancel_button.grid(row=0, column=2, padx=(8, 0))
        ttk.Label(self, textvariable=self.status_var, wraplength=700).grid(
            row=5, column=0, sticky="w", pady=(10, 0)
        )

    def _add_files(self, initial_dir: Path | None = None) -> None:
        selected = [Path(item) for item in filedialog.askopenfilenames(
            title="Selecciona videos MP4",
            initialdir=str(initial_dir or self.quick_folders["Descargas"]),
            filetypes=[("Videos MP4", "*.mp4")],
        )]
        self._add_paths(selected)

    def _add_paths(self, paths: list[Path]) -> None:
        valid, invalid = validate_video_paths(paths)
        added = 0
        for path in valid:
            if path not in self.files:
                self.files.append(path)
                self.file_list.insert(tk.END, str(path))
                added += 1
        if added:
            self.status_var.set(
                f"{len(self.files)} video(s) listo(s). Puedes agregar más o transcribir."
            )
        if invalid:
            messagebox.showwarning("Archivos omitidos", "Algunos archivos no eran MP4 válidos.")

    def _drop_enter(self, event):
        if not self.running:
            self.file_list.configure(background="#dbeafe")
        return event.action

    def _drop_leave(self, event):
        self.file_list.configure(background="#f8fafc")
        return event.action

    def _drop_files(self, event):
        self.file_list.configure(background="#f8fafc")
        if not self.running:
            paths = parse_dropped_paths(event.data, self.master.tk.splitlist)
            self._add_paths(paths)
        return event.action

    def _remove_selected(self) -> None:
        for index in reversed(self.file_list.curselection()):
            del self.files[index]
            self.file_list.delete(index)

    def _choose_destination(self) -> None:
        folder = filedialog.askdirectory(title="Carpeta para las transcripciones")
        if folder:
            self.destination_var.set(folder)

    def _start(self) -> None:
        if not self.files:
            messagebox.showinfo("Faltan videos", "Agrega al menos un video MP4.")
            return
        if not self.txt_var.get() and not self.srt_var.get():
            messagebox.showinfo("Falta formato", "Marca Texto, Subtítulos o ambos.")
            return
        self.running = True
        self.cancel_event.clear()
        self.progress["value"] = 0
        self.status_var.set("Preparando el modelo. La primera vez puede tardar por la descarga…")
        self._set_controls(False)
        files = tuple(self.files)
        model_name = MODELS[self.model_var.get()]
        language = LANGUAGES[self.language_var.get()]
        destination = Path(self.destination_var.get()) if self.destination_var.get() else None
        formats = (self.txt_var.get(), self.srt_var.get())
        threading.Thread(
            target=self._run_batch,
            args=(files, model_name, language, destination, formats),
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
                self.events.put(("status", f"Transcribiendo {source.name} ({index + 1}/{total})…"))
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
                self.events.put(("status", f"Guardado: {', '.join(path.name for path in created)} · idioma {detected}"))
            self.events.put(("done", f"Listo: {total} video(s) transcrito(s)."))
        except TranscriptionCancelled:
            self.events.put(("cancelled", "Transcripción cancelada."))
        except Exception as error:
            self.events.put(("error", str(error)))

    def _poll_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                kind, value = event
                if kind == "progress":
                    self.progress["value"] = value
                elif kind == "status":
                    self.status_var.set(value)
                elif kind in {"done", "cancelled", "error"}:
                    self.running = False
                    self._set_controls(True)
                    self.status_var.set(value)
                    if kind == "done":
                        self.progress["value"] = 100
                        messagebox.showinfo("Transcripción terminada", value)
                    elif kind == "error":
                        messagebox.showerror("No se pudo transcribir", value)
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def _set_controls(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for widget in (
            self.add_button,
            self.remove_button,
            self.choose_button,
            self.start_button,
            *self.folder_buttons,
        ):
            widget.configure(state=state)
        self.model_combo.configure(state="readonly" if enabled else "disabled")
        self.language_combo.configure(state="readonly" if enabled else "disabled")
        self.cancel_button.configure(state="disabled" if enabled else "normal")


def run() -> None:
    root = TkinterDnD.Tk()
    style = ttk.Style(root)
    style.configure("Title.TLabel", font=("Sans", 20, "bold"))
    style.configure("Subtitle.TLabel", foreground="#4b5563")
    style.configure("Hint.TLabel", foreground="#5f6368", font=("Sans", 9))
    style.configure("DropHint.TLabel", foreground="#1d4ed8", font=("Sans", 10, "bold"))
    style.configure("Accent.TButton", font=("Sans", 10, "bold"))
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
