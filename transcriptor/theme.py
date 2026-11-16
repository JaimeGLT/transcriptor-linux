"""Tema visual sobrio y consistente para la aplicación."""

from tkinter import ttk


COLORS = {
    "background": "#eef2f3",
    "surface": "#ffffff",
    "border": "#cbd5d8",
    "text": "#172326",
    "muted": "#5f6f73",
    "header": "#16383f",
    "accent": "#087f78",
    "accent_hover": "#076b66",
    "soft_accent": "#dff3f0",
    "drop": "#d9efed",
    "danger": "#a33a35",
}


def apply_theme(root) -> ttk.Style:
    root.configure(background=COLORS["background"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        ".",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=("Noto Sans", 10),
    )
    style.configure("App.TFrame", background=COLORS["background"])
    style.configure("Header.TFrame", background=COLORS["header"])
    style.configure(
        "HeaderTitle.TLabel",
        background=COLORS["header"],
        foreground="#ffffff",
        font=("Noto Sans", 22, "bold"),
    )
    style.configure(
        "HeaderSubtitle.TLabel",
        background=COLORS["header"],
        foreground="#d5e4e6",
        font=("Noto Sans", 10),
    )
    style.configure(
        "Privacy.TLabel",
        background=COLORS["header"],
        foreground="#96e0d4",
        font=("Noto Sans", 10, "bold"),
    )
    style.configure(
        "Card.TFrame",
        background=COLORS["surface"],
        relief="solid",
        borderwidth=1,
    )
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure(
        "CardTitle.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("Noto Sans", 12, "bold"),
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        font=("Noto Sans", 9),
    )
    style.configure(
        "FieldLabel.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("Noto Sans", 9, "bold"),
    )
    style.configure(
        "Empty.TLabel",
        background="#f7fafb",
        foreground=COLORS["muted"],
        font=("Noto Sans", 11),
        padding=24,
    )
    style.configure(
        "Drop.Empty.TLabel",
        background=COLORS["drop"],
        foreground=COLORS["accent"],
        font=("Noto Sans", 11, "bold"),
        padding=24,
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["accent"],
        foreground="#ffffff",
        borderwidth=0,
        padding=(18, 10),
        font=("Noto Sans", 10, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["accent_hover"]), ("disabled", "#9cb5b3")],
        foreground=[("disabled", "#edf4f3")],
    )
    style.configure(
        "Secondary.TButton",
        background="#edf3f4",
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        padding=(12, 7),
    )
    style.map("Secondary.TButton", background=[("active", "#dfe9ea")])
    style.configure(
        "Quiet.TButton",
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        borderwidth=0,
        padding=(8, 6),
    )
    style.map("Quiet.TButton", foreground=[("active", COLORS["text"])])
    style.configure(
        "Treeview",
        background="#fbfcfc",
        fieldbackground="#fbfcfc",
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        rowheight=30,
    )
    style.configure(
        "Treeview.Heading",
        background="#e7edef",
        foreground=COLORS["text"],
        relief="flat",
        font=("Noto Sans", 9, "bold"),
        padding=(8, 6),
    )
    style.map("Treeview", background=[("selected", COLORS["accent"])])
    style.configure(
        "TCombobox",
        fieldbackground="#ffffff",
        background="#ffffff",
        bordercolor=COLORS["border"],
        padding=6,
    )
    style.configure(
        "Surface.TRadiobutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.configure(
        "Surface.TCheckbutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.configure(
        "Accent.Horizontal.TProgressbar",
        troughcolor="#d7e2e3",
        background=COLORS["accent"],
        borderwidth=0,
        thickness=9,
    )
    return style
