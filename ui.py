import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
import threading
import time
import logging
import os
import sys
import queue
import json
from logging.handlers import RotatingFileHandler

from PIL import Image, ImageTk, ImageDraw, ImageFont

from file_sorter import sort_directory, undo, redo

# watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ttkbootstrap
try:
    import ttkbootstrap as tb
    from ttkbootstrap import Style, Window
except Exception:
    tb = None
    Style = None
    Window = None


# ============================================================
# LOGGER
# ============================================================

LOG_FILE = Path("sorted_files_log.txt")
SETTINGS_FILE = Path("organizer_settings.json")


def setup_logger(level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger("smart_organizer")
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(message)s"))

    fh = RotatingFileHandler(
        str(LOG_FILE),
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
        mode="a"
    )
    fh.setLevel(level)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
    )

    logger.handlers = []
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False

    return logger


logger = setup_logger()


# ============================================================
# DPI AWARENESS
# ============================================================

try:
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


# ============================================================
# COLORS
# ============================================================

COLORS = {
    "dark": {
        "background": "#0b1120",
        "surface": "#111827",
        "surface_2": "#172033",
        "surface_3": "#1e293b",
        "border": "#263449",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "primary": "#6366f1",
        "primary_hover": "#818cf8",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "cyan": "#06b6d4",
        "purple": "#8b5cf6",
        "log_bg": "#080d18",
        "log_fg": "#cbd5e1",
        "canvas": "#0b1120",
    },

    "light": {
        "background": "#f4f7fb",
        "surface": "#ffffff",
        "surface_2": "#f8fafc",
        "surface_3": "#eef2ff",
        "border": "#dbe3ef",
        "text": "#172033",
        "muted": "#64748b",
        "primary": "#4f46e5",
        "primary_hover": "#6366f1",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "cyan": "#0891b2",
        "purple": "#7c3aed",
        "log_bg": "#111827",
        "log_fg": "#d1d5db",
        "canvas": "#f4f7fb",
    }
}


# ============================================================
# FILE ICONS
# ============================================================

FILE_ICONS = {}

FILE_TYPE_COLORS = {
    ".txt": (56, 189, 248, 255),
    ".py": (250, 204, 21, 255),
    ".jpg": (251, 146, 60, 255),
    ".jpeg": (251, 146, 60, 255),
    ".png": (74, 222, 128, 255),
    ".pdf": (248, 113, 113, 255),
    ".mp3": (244, 114, 182, 255),
    ".mp4": (251, 146, 60, 255),
    ".zip": (168, 85, 247, 255),
    ".rar": (168, 85, 247, 255),
    ".doc": (59, 130, 246, 255),
    ".docx": (59, 130, 246, 255),
    ".xls": (34, 197, 94, 255),
    ".xlsx": (34, 197, 94, 255),
}


def get_file_icon(file_path: Path, size=(56, 56)):
    """
    Creates a simple modern icon/thumbnail for files and directories.
    """

    suffix = file_path.suffix.lower()
    key = ("DIR" if file_path.is_dir() else suffix)

    # Do not cache real image thumbnails by extension.
    # Otherwise every JPG would display the same image.
    cacheable = not (
        suffix in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
        and file_path.is_file()
    )

    if cacheable and key in FILE_ICONS:
        return FILE_ICONS[key]

    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # --------------------------------------------------------
    # DIRECTORY
    # --------------------------------------------------------

    if file_path.is_dir():

        # Shadow
        draw.rounded_rectangle(
            [5, 10, size[0] - 3, size[1] - 3],
            radius=7,
            fill=(15, 23, 42, 80)
        )

        # Folder
        draw.rounded_rectangle(
            [4, 13, size[0] - 4, size[1] - 5],
            radius=7,
            fill=(99, 102, 241, 255)
        )

        draw.rounded_rectangle(
            [7, 7, 27, 18],
            radius=4,
            fill=(129, 140, 248, 255)
        )

        txt = "DIR"

        bbox = draw.textbbox((0, 0), txt, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(
            ((size[0] - w) / 2, (size[1] - h) / 2 + 5),
            txt,
            fill="white",
            font=font
        )

    # --------------------------------------------------------
    # IMAGE THUMBNAIL
    # --------------------------------------------------------

    elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]:

        try:
            im = Image.open(file_path).convert("RGBA")
            im.thumbnail((size[0] - 4, size[1] - 4), Image.LANCZOS)

            thumb = Image.new("RGBA", size, (30, 41, 59, 255))

            x = (size[0] - im.width) // 2
            y = (size[1] - im.height) // 2

            thumb.paste(im, (x, y), im)

            return thumb

        except Exception:
            pass

        color = FILE_TYPE_COLORS.get(
            suffix,
            (148, 163, 184, 255)
        )

        draw.rounded_rectangle(
            [2, 2, size[0] - 2, size[1] - 2],
            radius=9,
            fill=color
        )

    # --------------------------------------------------------
    # NORMAL FILE
    # --------------------------------------------------------

    else:

        color = FILE_TYPE_COLORS.get(
            suffix,
            (100, 116, 139, 255)
        )

        # file background
        draw.rounded_rectangle(
            [3, 3, size[0] - 3, size[1] - 3],
            radius=9,
            fill=color
        )

        # folded corner
        draw.polygon(
            [
                (size[0] - 18, 3),
                (size[0] - 3, 18),
                (size[0] - 18, 18)
            ],
            fill=(255, 255, 255, 110)
        )

        txt = suffix[1:].upper() if suffix else "FILE"

        if len(txt) > 5:
            txt = txt[:5]

        bbox = draw.textbbox((0, 0), txt, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(
            ((size[0] - w) / 2, (size[1] - h) / 2 + 4),
            txt,
            fill="white",
            font=font
        )

    if cacheable:
        FILE_ICONS[key] = img

    return img


# ============================================================
# WATCHDOG
# ============================================================

class FolderChangeHandler(FileSystemEventHandler):

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        self.callback()


# ============================================================
# TOOLTIP
# ============================================================

class ToolTip:

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):

        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)

        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#111827",
            foreground="#f8fafc",
            relief=tk.FLAT,
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        label.pack(ipadx=8, ipady=5)

    def hide_tip(self, event=None):

        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ============================================================
# APPLICATION
# ============================================================

class SmartOrganizerApp:

    THUMB_SIZE = (56, 56)

    def __init__(self, root):

        self.root = root

        self.root.title("Smart File Organizer")
        self.root.geometry("1180x850")
        self.root.minsize(950, 700)

        # ----------------------------------------------------
        # THEME
        # ----------------------------------------------------

        if tb:
            self.style = Style()
        else:
            self.style = ttk.Style()

        self.current_theme = "dark"

        self._load_initial_theme()

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.selected_dir = tk.StringVar()

        self.preserve_structure = tk.BooleanVar(value=True)
        self.dry_run = tk.BooleanVar(value=False)
        self.include_hidden = tk.BooleanVar(value=False)
        self.compute_duplicates = tk.BooleanVar(value=False)

        self.include_suffixes = tk.StringVar()

        self.progress_value = tk.IntVar(value=0)

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.log_queue = queue.Queue()

        self.preview_images = []

        self.observer = None

        self.total_files = 0
        self.moved_files = 0
        self.duplicate_files = 0

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self._build_ui()

        self._attach_auto_save_traces()

        self._load_settings()

        self.root.after(200, self._process_log_queue)

        self.canvas.bind(
            "<Configure>",
            self._on_canvas_resize
        )

    # ========================================================
    # THEME
    # ========================================================

    def _load_initial_theme(self):

        if tb:

            try:
                self.style.theme_use("darkly")
            except Exception:
                pass

    def _colors(self):
        return COLORS["dark"] if self.current_theme == "dark" else COLORS["light"]

    def toggle_theme(self):

        new_theme = (
            "light"
            if self.current_theme == "dark"
            else "dark"
        )

        self.current_theme = new_theme

        try:

            if tb:

                bootstrap_theme = (
                    "darkly"
                    if new_theme == "dark"
                    else "flatly"
                )

                self.style.theme_use(bootstrap_theme)

            self._configure_styles()
            self._apply_theme_adjustments()
            self.refresh_preview()

            self._save_settings(auto=True)

        except Exception as e:

            logger.exception("Failed to toggle theme")

            messagebox.showerror(
                "Theme Error",
                f"Could not change theme:\n{e}"
            )

    # ========================================================
    # STYLES
    # ========================================================

    def _configure_styles(self):

        c = self._colors()

        style = self.style

        # ----------------------------------------------------
        # Frames
        # ----------------------------------------------------

        style.configure(
            "App.TFrame",
            background=c["background"]
        )

        style.configure(
            "Card.TFrame",
            background=c["surface"]
        )

        style.configure(
            "Inner.TFrame",
            background=c["surface_2"]
        )

        # ----------------------------------------------------
        # Labels
        # ----------------------------------------------------

        style.configure(
            "Title.TLabel",
            background=c["background"],
            foreground=c["text"],
            font=("Segoe UI", 22, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=c["background"],
            foreground=c["muted"],
            font=("Segoe UI", 10)
        )

        style.configure(
            "Section.TLabel",
            background=c["surface"],
            foreground=c["text"],
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Muted.TLabel",
            background=c["surface"],
            foreground=c["muted"],
            font=("Segoe UI", 9)
        )

        style.configure(
            "Stats.TLabel",
            background=c["surface"],
            foreground=c["text"],
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "StatsCaption.TLabel",
            background=c["surface"],
            foreground=c["muted"],
            font=("Segoe UI", 9)
        )

        style.configure(
            "Status.TLabel",
            background=c["surface"],
            foreground=c["muted"],
            font=("Segoe UI", 9)
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 10)
        )

        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10),
            padding=(12, 8)
        )

        style.configure(
            "Small.TButton",
            font=("Segoe UI", 9),
            padding=(9, 6)
        )

        # ----------------------------------------------------
        # Checkbuttons
        # ----------------------------------------------------

        style.configure(
            "Modern.TCheckbutton",
            background=c["surface"],
            foreground=c["text"],
            font=("Segoe UI", 9)
        )

        # ----------------------------------------------------
        # Entry
        # ----------------------------------------------------

        style.configure(
            "Modern.TEntry",
            padding=9,
            font=("Segoe UI", 10)
        )

        # ----------------------------------------------------
        # Progressbar
        # ----------------------------------------------------

        try:

            style.configure(
                "Modern.Horizontal.TProgressbar",
                thickness=9
            )

        except Exception:
            pass

    def _apply_theme_adjustments(self):

        c = self._colors()

        try:

            self.root.configure(
                background=c["background"]
            )

            self.output.configure(
                bg=c["log_bg"],
                fg=c["log_fg"],
                insertbackground="#ffffff",
                selectbackground=c["primary"],
                selectforeground="#ffffff"
            )

            self.canvas.configure(
                bg=c["canvas"]
            )

            self.preview_frame.configure(
                style="App.TFrame"
            )

            self.inner_frame.configure(
                style="Inner.TFrame"
            )

        except Exception:
            pass

    # ========================================================
    # BUILD UI
    # ========================================================

    def _build_ui(self):

        self._configure_styles()

        c = self._colors()

        # Main root
        self.main = ttk.Frame(
            self.root,
            style="App.TFrame",
            padding=18
        )

        self.main.pack(
            fill=tk.BOTH,
            expand=True
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        header.pack(
            fill=tk.X,
            pady=(0, 16)
        )

        # left side
        title_frame = ttk.Frame(
            header,
            style="App.TFrame"
        )

        title_frame.pack(
            side=tk.LEFT
        )

        ttk.Label(
            title_frame,
            text="Smart File Organizer",
            style="Title.TLabel"
        ).pack(
            anchor=tk.W
        )

        ttk.Label(
            title_frame,
            text="Organize your files. Keep your workspace clean.",
            style="Subtitle.TLabel"
        ).pack(
            anchor=tk.W,
            pady=(2, 0)
        )

        # right side
        header_buttons = ttk.Frame(
            header,
            style="App.TFrame"
        )

        header_buttons.pack(
            side=tk.RIGHT,
            pady=4
        )

        self.theme_btn = ttk.Button(
            header_buttons,
            text="☀  Light / Dark",
            command=self.toggle_theme,
            style="Small.TButton"
        )

        self.theme_btn.pack(
            side=tk.LEFT,
            padx=4
        )

        self.settings_btn = ttk.Button(
            header_buttons,
            text="⚙  Settings",
            command=self.open_settings_window,
            style="Small.TButton"
        )

        self.settings_btn.pack(
            side=tk.LEFT,
            padx=4
        )

        # ====================================================
        # FOLDER CARD
        # ====================================================

        folder_card = ttk.Frame(
            self.main,
            style="Card.TFrame",
            padding=16
        )

        folder_card.pack(
            fill=tk.X,
            pady=(0, 12)
        )

        ttk.Label(
            folder_card,
            text="TARGET FOLDER",
            style="Section.TLabel"
        ).pack(
            anchor=tk.W
        )

        folder_row = ttk.Frame(
            folder_card,
            style="Card.TFrame"
        )

        folder_row.pack(
            fill=tk.X,
            pady=(8, 0)
        )

        folder_icon = ttk.Label(
            folder_row,
            text="📁",
            background=c["surface"],
            foreground=c["text"],
            font=("Segoe UI Emoji", 22)
        )

        folder_icon.pack(
            side=tk.LEFT,
            padx=(0, 10)
        )

        self.dir_entry = ttk.Entry(
            folder_row,
            textvariable=self.selected_dir,
            style="Modern.TEntry"
        )

        self.dir_entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True
        )

        ttk.Button(
            folder_row,
            text="Browse",
            command=self.browse_folder,
            style="Action.TButton"
        ).pack(
            side=tk.LEFT,
            padx=(8, 0)
        )

        # ====================================================
        # OPTIONS + ACTIONS
        # ====================================================

        middle = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        middle.pack(
            fill=tk.X,
            pady=(0, 12)
        )

        # ----------------------------------------------------
        # OPTIONS CARD
        # ----------------------------------------------------

        options_card = ttk.Frame(
            middle,
            style="Card.TFrame",
            padding=14
        )

        options_card.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=(0, 6)
        )

        ttk.Label(
            options_card,
            text="OPTIONS",
            style="Section.TLabel"
        ).pack(
            anchor=tk.W,
            pady=(0, 8)
        )

        options_grid = ttk.Frame(
            options_card,
            style="Card.TFrame"
        )

        options_grid.pack(
            fill=tk.X
        )

        self._make_checkbutton(
            options_grid,
            "Preserve folder structure",
            self.preserve_structure,
            0,
            0
        )

        self._make_checkbutton(
            options_grid,
            "Dry run — preview only",
            self.dry_run,
            0,
            1
        )

        self._make_checkbutton(
            options_grid,
            "Include hidden files",
            self.include_hidden,
            1,
            0
        )

        self._make_checkbutton(
            options_grid,
            "Detect duplicates",
            self.compute_duplicates,
            1,
            1
        )

        ttk.Label(
            options_card,
            text="File types filter  •  .png, .jpg, .pdf",
            style="Muted.TLabel"
        ).pack(
            anchor=tk.W,
            pady=(12, 3)
        )

        ttk.Entry(
            options_card,
            textvariable=self.include_suffixes,
            style="Modern.TEntry"
        ).pack(
            fill=tk.X
        )

        # ----------------------------------------------------
        # ACTION CARD
        # ----------------------------------------------------

        action_card = ttk.Frame(
            middle,
            style="Card.TFrame",
            padding=14
        )

        action_card.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=(6, 0)
        )

        ttk.Label(
            action_card,
            text="ACTIONS",
            style="Section.TLabel"
        ).pack(
            anchor=tk.W,
            pady=(0, 8)
        )

        self.sort_btn = ttk.Button(
            action_card,
            text="▶  SORT FILES",
            command=self.on_sort,
            style="Primary.TButton"
        )

        self.sort_btn.pack(
            fill=tk.X,
            pady=(0, 8)
        )

        action_row = ttk.Frame(
            action_card,
            style="Card.TFrame"
        )

        action_row.pack(
            fill=tk.X
        )

        ttk.Button(
            action_row,
            text="↶ Undo",
            command=self.on_undo,
            style="Small.TButton"
        ).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(0, 3)
        )

        ttk.Button(
            action_row,
            text="↷ Redo",
            command=self.on_redo,
            style="Small.TButton"
        ).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=3
        )

        ttk.Button(
            action_row,
            text="📂 Open",
            command=self.open_folder,
            style="Small.TButton"
        ).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(3, 0)
        )

        # ====================================================
        # STATS
        # ====================================================

        stats_frame = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        stats_frame.pack(
            fill=tk.X,
            pady=(0, 12)
        )

        self.stats_total = self._create_stat_card(
            stats_frame,
            "FILES SCANNED",
            "0",
            "📄"
        )

        self.stats_moved = self._create_stat_card(
            stats_frame,
            "FILES MOVED",
            "0",
            "↗"
        )

        self.stats_duplicates = self._create_stat_card(
            stats_frame,
            "DUPLICATES",
            "0",
            "♢"
        )

        self.stats_status = self._create_stat_card(
            stats_frame,
            "STATUS",
            "READY",
            "●"
        )

        # ====================================================
        # PROGRESS
        # ====================================================

        progress_card = ttk.Frame(
            self.main,
            style="Card.TFrame",
            padding=(14, 10)
        )

        progress_card.pack(
            fill=tk.X,
            pady=(0, 12)
        )

        progress_top = ttk.Frame(
            progress_card,
            style="Card.TFrame"
        )

        progress_top.pack(
            fill=tk.X
        )

        ttk.Label(
            progress_top,
            text="ORGANIZATION PROGRESS",
            style="Section.TLabel"
        ).pack(
            side=tk.LEFT
        )

        self.progress_percent = ttk.Label(
            progress_top,
            text="0%",
            style="Muted.TLabel"
        )

        self.progress_percent.pack(
            side=tk.RIGHT
        )

        self.progress = ttk.Progressbar(
            progress_card,
            mode="determinate",
            variable=self.progress_value,
            maximum=100,
            style="Modern.Horizontal.TProgressbar"
        )

        self.progress.pack(
            fill=tk.X,
            pady=(7, 3)
        )

        self.status_label = ttk.Label(
            progress_card,
            text="Ready — select a folder to begin.",
            style="Status.TLabel"
        )

        self.status_label.pack(
            anchor=tk.W
        )

        # ====================================================
        # LOWER AREA
        # ====================================================

        lower = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        lower.pack(
            fill=tk.BOTH,
            expand=True
        )

        # ----------------------------------------------------
        # LOG CARD
        # ----------------------------------------------------

        log_card = ttk.Frame(
            lower,
            style="Card.TFrame",
            padding=10
        )

        log_card.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=False,
            ipadx=2,
            padx=(0, 6)
        )

        log_card.configure(width=420)

        log_header = ttk.Frame(
            log_card,
            style="Card.TFrame"
        )

        log_header.pack(
            fill=tk.X,
            pady=(0, 6)
        )

        ttk.Label(
            log_header,
            text="ACTIVITY LOG",
            style="Section.TLabel"
        ).pack(
            side=tk.LEFT
        )

        ttk.Button(
            log_header,
            text="Clear",
            command=self.clear_log,
            style="Small.TButton"
        ).pack(
            side=tk.RIGHT
        )

        self.output = scrolledtext.ScrolledText(
            log_card,
            height=12,
            bg=c["log_bg"],
            fg=c["log_fg"],
            insertbackground="#ffffff",
            selectbackground=c["primary"],
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            font=("Cascadia Mono", 9)
        )

        self.output.pack(
            fill=tk.BOTH,
            expand=True
        )

        # ----------------------------------------------------
        # PREVIEW CARD
        # ----------------------------------------------------

        preview_card = ttk.Frame(
            lower,
            style="Card.TFrame",
            padding=10
        )

        preview_card.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=(6, 0)
        )

        preview_header = ttk.Frame(
            preview_card,
            style="Card.TFrame"
        )

        preview_header.pack(
            fill=tk.X,
            pady=(0, 6)
        )

        ttk.Label(
            preview_header,
            text="FOLDER PREVIEW",
            style="Section.TLabel"
        ).pack(
            side=tk.LEFT
        )

        ttk.Label(
            preview_header,
            text="Live",
            style="Muted.TLabel"
        ).pack(
            side=tk.RIGHT
        )

        self.preview_frame = ttk.Frame(
            preview_card,
            style="Inner.TFrame"
        )

        self.preview_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.canvas = tk.Canvas(
            self.preview_frame,
            bg=c["canvas"],
            highlightthickness=0,
            borderwidth=0
        )

        self.scrollbar = ttk.Scrollbar(
            self.preview_frame,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.canvas.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.inner_frame = ttk.Frame(
            self.canvas,
            style="Inner.TFrame"
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw",
            width=400
        )

        self.canvas.bind(
            "<Configure>",
            self._on_canvas_resize
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        footer.pack(
            fill=tk.X,
            pady=(10, 0)
        )

        ttk.Label(
            footer,
            text="Smart File Organizer  •  Automatic settings  •  Live folder monitoring",
            style="Subtitle.TLabel"
        ).pack(
            side=tk.LEFT
        )

        ttk.Button(
            footer,
            text="Save Settings",
            command=self._save_settings,
            style="Small.TButton"
        ).pack(
            side=tk.RIGHT
        )

        self._apply_theme_adjustments()

    # ========================================================
    # UI HELPERS
    # ========================================================

    def _make_checkbutton(
        self,
        parent,
        text,
        variable,
        row,
        column
    ):

        cb = ttk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            style="Modern.TCheckbutton"
        )

        cb.grid(
            row=row,
            column=column,
            sticky="w",
            padx=(0, 18),
            pady=4
        )

    def _create_stat_card(
        self,
        parent,
        title,
        value,
        icon
    ):

        card = ttk.Frame(
            parent,
            style="Card.TFrame",
            padding=12
        )

        card.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=4
        )

        top = ttk.Frame(
            card,
            style="Card.TFrame"
        )

        top.pack(
            fill=tk.X
        )

        ttk.Label(
            top,
            text=icon,
            background=self._colors()["surface"],
            foreground=self._colors()["primary"],
            font=("Segoe UI Emoji", 16)
        ).pack(
            side=tk.LEFT,
            padx=(0, 8)
        )

        ttk.Label(
            top,
            text=title,
            style="StatsCaption.TLabel"
        ).pack(
            side=tk.LEFT
        )

        value_label = ttk.Label(
            card,
            text=value,
            style="Stats.TLabel"
        )

        value_label.pack(
            anchor=tk.W,
            pady=(4, 0)
        )

        return value_label

    # ========================================================
    # AUTO SAVE
    # ========================================================

    def _attach_auto_save_traces(self):

        try:

            variables = (
                self.preserve_structure,
                self.dry_run,
                self.include_hidden,
                self.compute_duplicates,
                self.selected_dir,
                self.include_suffixes
            )

            for var in variables:

                var.trace_add(
                    "write",
                    lambda *args: self._save_settings(auto=True)
                )

        except Exception:
            pass

    # ========================================================
    # FOLDER
    # ========================================================

    def browse_folder(self):

        path = filedialog.askdirectory()

        if path:

            self.selected_dir.set(path)

            self.refresh_preview()

            self.start_watchdog()

            self._enqueue_log(
                f"Selected folder: {path}"
            )

            self._save_settings(auto=True)

    def open_folder(self):

        path = self.selected_dir.get()

        if not path:

            messagebox.showwarning(
                "No folder",
                "Please select a folder first."
            )

            return

        try:

            if sys.platform.startswith("win"):

                os.startfile(path)

            elif sys.platform == "darwin":

                import subprocess
                subprocess.Popen(["open", path])

            else:

                import subprocess
                subprocess.Popen(["xdg-open", path])

        except Exception as e:

            messagebox.showerror(
                "Open folder failed",
                str(e)
            )

    # ========================================================
    # SORT
    # ========================================================

    def on_sort(self):

        folder = self.selected_dir.get()

        if not folder:

            messagebox.showwarning(
                "No folder",
                "Please select a folder first."
            )

            return

        if not Path(folder).exists():

            messagebox.showerror(
                "Folder not found",
                "The selected folder does not exist."
            )

            return

        self.sort_btn.config(
            state=tk.DISABLED
        )

        self.status_label.config(
            text="Scanning files...",
            foreground=self._colors()["primary"]
        )

        self.progress_value.set(0)

        self.progress_percent.config(
            text="0%"
        )

        self.stats_status.config(
            text="RUNNING"
        )

        thread = threading.Thread(
            target=self._sort_worker,
            args=(folder,),
            daemon=True
        )

        thread.start()

    def _sort_worker(self, folder):

        dest_root = Path(folder)

        suffix_filter = [
            s.strip().lower()
            for s in self.include_suffixes.get().split(",")
            if s.strip()
        ]

        self._enqueue_log(
            f"▶ Starting sorting: {folder}"
        )

        def progress_cb(processed, total):

            pct = (
                int((processed / total) * 100)
                if total
                else 100
            )

            self.root.after(
                0,
                lambda: self._update_progress(pct)
            )

            self.root.after(
                0,
                self.refresh_preview
            )

        try:

            summary = sort_directory(
                root_dir=Path(folder),
                dest_root=dest_root,
                preserve_structure=self.preserve_structure.get(),
                dry_run=self.dry_run.get(),
                include_hidden=self.include_hidden.get(),
                exclude_patterns=None,
                min_size_bytes=0,
                max_size_bytes=None,
                compute_duplicates=self.compute_duplicates.get(),
                progress_callback=progress_cb,
                suffix_filter=suffix_filter
            )

            moved = summary["moved_count"]
            total = summary["total_files"]

            duration = summary.get(
                "duration_seconds",
                0.0
            )

            dup = summary.get(
                "duplicate_count",
                0
            )

            self._enqueue_log(
                f"✓ Done | Scanned: {total} | "
                f"Moved: {moved} | "
                f"Duplicates: {dup} | "
                f"Time: {duration:.2f}s"
            )

            for src, dst, moved_flag in summary["moved_items"][:80]:

                prefix = (
                    "MOVED"
                    if moved_flag
                    else "[DRY]"
                )

                self._enqueue_log(
                    f"{prefix}: {src} → {dst}"
                )

            if len(summary["moved_items"]) > 80:

                self._enqueue_log(
                    f"... and "
                    f"{len(summary['moved_items']) - 80} "
                    f"more entries"
                )

            self.root.after(
                0,
                lambda: self._update_stats(
                    total,
                    moved,
                    dup
                )
            )

        except Exception as e:

            logger.exception(
                "Error during sorting"
            )

            self._enqueue_log(
                f"✕ Error: {e}"
            )

        finally:

            self.root.after(
                0,
                self._finish_sort
            )

    # ========================================================
    # PREVIEW
    # ========================================================

    def refresh_preview(self):

        folder = self.selected_dir.get()

        if not folder or not Path(folder).exists():
            return

        try:

            for widget in self.inner_frame.winfo_children():
                widget.destroy()

            self.preview_images.clear()

            items = sorted(
                Path(folder).iterdir(),
                key=lambda p: (
                    not p.is_dir(),
                    p.name.lower()
                )
            )

            canvas_width = max(
                self.canvas.winfo_width(),
                420
            )

            cell_width = 105

            cols = max(
                1,
                canvas_width // cell_width
            )

            c = self._colors()

            for idx, item in enumerate(items):

                frame = tk.Frame(
                    self.inner_frame,
                    bg=c["surface_2"],
                    width=95,
                    height=95
                )

                row = idx // cols
                col = idx % cols

                frame.grid(
                    row=row,
                    column=col,
                    padx=7,
                    pady=7,
                    sticky="n"
                )

                frame.grid_propagate(False)

                # ------------------------------------------------
                # ICON
                # ------------------------------------------------

                thumb_img = get_file_icon(
                    item,
                    size=self.THUMB_SIZE
                )

                thumb = ImageTk.PhotoImage(
                    thumb_img
                )

                lbl = tk.Label(
                    frame,
                    image=thumb,
                    bg=c["surface_2"],
                    cursor="hand2",
                    borderwidth=0
                )

                lbl.image = thumb

                lbl.pack(
                    pady=(8, 3)
                )

                ToolTip(
                    lbl,
                    text=item.name
                )

                # ------------------------------------------------
                # NAME
                # ------------------------------------------------

                name = item.name

                if len(name) > 14:

                    name = (
                        name[:12]
                        + "…"
                    )

                name_lbl = tk.Label(
                    frame,
                    text=name,
                    bg=c["surface_2"],
                    fg=c["text"],
                    font=("Segoe UI", 8),
                    wraplength=88,
                    justify="center"
                )

                name_lbl.pack(
                    fill=tk.X,
                    padx=4
                )

                # ------------------------------------------------
                # HOVER
                # ------------------------------------------------

                def on_enter(
                    event,
                    f=frame,
                    label=lbl,
                    name_label=name_lbl
                ):

                    f.configure(
                        bg=c["surface_3"]
                    )

                    label.configure(
                        bg=c["surface_3"]
                    )

                    name_label.configure(
                        bg=c["surface_3"]
                    )

                def on_leave(
                    event,
                    f=frame,
                    label=lbl,
                    name_label=name_lbl
                ):

                    f.configure(
                        bg=c["surface_2"]
                    )

                    label.configure(
                        bg=c["surface_2"]
                    )

                    name_label.configure(
                        bg=c["surface_2"]
                    )

                frame.bind(
                    "<Enter>",
                    on_enter
                )

                frame.bind(
                    "<Leave>",
                    on_leave
                )

                lbl.bind(
                    "<Enter>",
                    on_enter
                )

                lbl.bind(
                    "<Leave>",
                    on_leave
                )

                name_lbl.bind(
                    "<Enter>",
                    on_enter
                )

                name_lbl.bind(
                    "<Leave>",
                    on_leave
                )

                self.preview_images.append(
                    thumb
                )

            for c_index in range(cols):

                self.inner_frame.columnconfigure(
                    c_index,
                    weight=1
                )

            self.canvas.update_idletasks()

            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )

        except Exception as e:

            logger.exception(
                "Preview refresh failed"
            )

    # ========================================================
    # CANVAS RESIZE
    # ========================================================

    def _on_canvas_resize(self, event=None):

        try:

            self.canvas.itemconfig(
                self.canvas_window,
                width=self.canvas.winfo_width()
            )

        except Exception:
            pass

        if hasattr(
            self,
            "_resize_after_id"
        ):

            try:

                self.root.after_cancel(
                    self._resize_after_id
                )

            except Exception:
                pass

        self._resize_after_id = self.root.after(
            300,
            self.refresh_preview
        )

    # ========================================================
    # WATCHDOG
    # ========================================================

    def start_watchdog(self):

        if self.observer:

            try:

                self.observer.stop()
                self.observer.join(timeout=1)

            except Exception:
                pass

            self.observer = None

        folder = self.selected_dir.get()

        if not folder:
            return

        event_handler = FolderChangeHandler(
            lambda: self._schedule_refresh()
        )

        self.observer = Observer()

        try:

            self.observer.schedule(
                event_handler,
                folder,
                recursive=False
            )

            self.observer.start()

            self._enqueue_log(
                "● Live folder monitoring enabled."
            )

        except Exception as e:

            self._enqueue_log(
                f"Watchdog failed to start: {e}"
            )

    # ========================================================
    # LOGGING
    # ========================================================

    def _enqueue_log(self, msg):

        timestamp = time.strftime(
            "[%H:%M:%S]"
        )

        self.log_queue.put(
            f"{timestamp} {msg}"
        )

    def _process_log_queue(self):

        while True:

            try:

                line = self.log_queue.get_nowait()

            except queue.Empty:
                break

            self.output.insert(
                tk.END,
                line + "\n"
            )

            self.output.see(
                tk.END
            )

        self.root.after(
            200,
            self._process_log_queue
        )

    # ========================================================
    # UNDO
    # ========================================================

    def on_undo(self):

        folder = self.selected_dir.get()

        if not folder:

            messagebox.showwarning(
                "No folder",
                "Please select a folder first."
            )

            return

        confirm = messagebox.askyesno(
            "Undo Last Operation",
            "Are you sure you want to undo the last sort operation?"
        )

        if not confirm:
            return

        self._enqueue_log(
            "↶ Attempting undo..."
        )

        thread = threading.Thread(
            target=self._undo_worker,
            args=(Path(folder),),
            daemon=True
        )

        thread.start()

    def _undo_worker(self, dest_root: Path):

        try:

            result = undo(dest_root)

            if result.get("errors"):

                for error in result["errors"]:

                    self._enqueue_log(
                        f"UNDO ERROR: {error}"
                    )

            self._enqueue_log(
                f"✓ Undone moves: "
                f"{result.get('undone', 0)}"
            )

            if result.get("removed_dirs"):

                for directory in result["removed_dirs"]:

                    self._enqueue_log(
                        f"Removed empty dir: {directory}"
                    )

            self.root.after(
                0,
                lambda: self._update_stats(
                    0,
                    0,
                    0
                )
            )

            self.root.after(
                0,
                self.refresh_preview
            )

        except Exception as e:

            logger.exception(
                "Undo error"
            )

            self._enqueue_log(
                f"Undo failed: {e}"
            )

    # ========================================================
    # REDO
    # ========================================================

    def on_redo(self):

        folder = self.selected_dir.get()

        if not folder:

            messagebox.showwarning(
                "No folder",
                "Please select a folder first."
            )

            return

        self._enqueue_log(
            "↷ Attempting redo..."
        )

        thread = threading.Thread(
            target=self._redo_worker,
            args=(Path(folder),),
            daemon=True
        )

        thread.start()

    def _redo_worker(self, dest_root: Path):

        try:

            result = redo(dest_root)

            if result.get("errors"):

                for error in result["errors"]:

                    self._enqueue_log(
                        f"REDO ERROR: {error}"
                    )

            self._enqueue_log(
                f"✓ Redone moves: "
                f"{result.get('redone', 0)}"
            )

            if result.get("created_dirs"):

                for directory in result["created_dirs"]:

                    self._enqueue_log(
                        f"Re-created dir: {directory}"
                    )

            self.root.after(
                0,
                lambda: self._update_stats(
                    0,
                    0,
                    0
                )
            )

            self.root.after(
                0,
                self.refresh_preview
            )

        except Exception as e:

            logger.exception(
                "Redo error"
            )

            self._enqueue_log(
                f"Redo failed: {e}"
            )

    # ========================================================
    # MISC
    # ========================================================

    def clear_log(self):

        self.output.delete(
            "1.0",
            tk.END
        )

    def _update_stats(
        self,
        total,
        moved,
        dup
    ):

        self.total_files = total
        self.moved_files = moved
        self.duplicate_files = dup

        self.stats_total.config(
            text=str(total)
        )

        self.stats_moved.config(
            text=str(moved)
        )

        self.stats_duplicates.config(
            text=str(dup)
        )

    # ========================================================
    # PROGRESS
    # ========================================================

    def _update_progress(self, pct):

        self.progress_value.set(
            pct
        )

        self.progress_percent.config(
            text=f"{pct}%"
        )

        self.status_label.config(
            text=f"Organizing files... {pct}%"
        )

    def _finish_sort(self):

        self.progress_value.set(
            100
        )

        self.progress_percent.config(
            text="100%"
        )

        self.sort_btn.config(
            state=tk.NORMAL
        )

        self.status_label.config(
            text="Organization completed successfully ✓"
        )

        self.stats_status.config(
            text="DONE"
        )

        self.root.after(
            1200,
            lambda: self.progress_value.set(0)
        )

        self.root.after(
            1200,
            lambda: self.progress_percent.config(
                text="0%"
            )
        )

        self.refresh_preview()

    # ========================================================
    # SETTINGS
    # ========================================================

    def _save_settings(self, auto=False):

        data = {
            "last_folder": self.selected_dir.get(),
            "preserve_structure": self.preserve_structure.get(),
            "dry_run": self.dry_run.get(),
            "include_hidden": self.include_hidden.get(),
            "compute_duplicates": self.compute_duplicates.get(),
            "include_suffixes": self.include_suffixes.get(),
            "theme": self.current_theme
        }

        try:

            with SETTINGS_FILE.open(
                "w",
                encoding="utf-8"
            ) as fh:

                json.dump(
                    data,
                    fh,
                    ensure_ascii=False,
                    indent=2
                )

            if not auto:

                self._enqueue_log(
                    "✓ Settings saved."
                )

        except Exception as e:

            self._enqueue_log(
                f"Failed to save settings: {e}"
            )

    def _load_settings(self):

        if not SETTINGS_FILE.exists():
            return

        try:

            with SETTINGS_FILE.open(
                "r",
                encoding="utf-8"
            ) as fh:

                data = json.load(fh)

            self.selected_dir.set(
                data.get(
                    "last_folder",
                    ""
                )
            )

            self.preserve_structure.set(
                data.get(
                    "preserve_structure",
                    True
                )
            )

            self.dry_run.set(
                data.get(
                    "dry_run",
                    False
                )
            )

            self.include_hidden.set(
                data.get(
                    "include_hidden",
                    False
                )
            )

            self.compute_duplicates.set(
                data.get(
                    "compute_duplicates",
                    False
                )
            )

            self.include_suffixes.set(
                data.get(
                    "include_suffixes",
                    ""
                )
            )

            theme = data.get(
                "theme"
            )

            if theme in (
                "dark",
                "light"
            ):

                self.current_theme = theme

                if tb:

                    bootstrap_theme = (
                        "darkly"
                        if theme == "dark"
                        else "flatly"
                    )

                    try:

                        self.style.theme_use(
                            bootstrap_theme
                        )

                    except Exception:
                        pass

            self._configure_styles()
            self._apply_theme_adjustments()

            self._enqueue_log(
                "✓ Settings loaded."
            )

            self.refresh_preview()

            if (
                self.selected_dir.get()
                and Path(
                    self.selected_dir.get()
                ).exists()
            ):

                self.start_watchdog()

        except Exception as e:

            self._enqueue_log(
                f"Failed to load settings: {e}"
            )

    # ========================================================
    # REFRESH SCHEDULER
    # ========================================================

    def _schedule_refresh(self):

        if hasattr(
            self,
            "_refresh_after_id"
        ):

            try:

                self.root.after_cancel(
                    self._refresh_after_id
                )

            except Exception:
                pass

        self._refresh_after_id = self.root.after(
            400,
            self.refresh_preview
        )

    # ========================================================
    # SETTINGS WINDOW
    # ========================================================

    def open_settings_window(self):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "Smart Organizer — Settings"
        )

        win.geometry(
            "520x470"
        )

        win.minsize(
            500,
            450
        )

        win.transient(
            self.root
        )

        c = self._colors()

        win.configure(
            background=c["background"]
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = tk.Frame(
            win,
            bg=c["background"]
        )

        header.pack(
            fill=tk.X,
            padx=22,
            pady=(20, 12)
        )

        tk.Label(
            header,
            text="Settings",
            bg=c["background"],
            fg=c["text"],
            font=("Segoe UI", 20, "bold")
        ).pack(
            anchor=tk.W
        )

        tk.Label(
            header,
            text="Configure how Smart File Organizer behaves.",
            bg=c["background"],
            fg=c["muted"],
            font=("Segoe UI", 9)
        ).pack(
            anchor=tk.W,
            pady=(2, 0)
        )

        # ----------------------------------------------------
        # Main card
        # ----------------------------------------------------

        card = tk.Frame(
            win,
            bg=c["surface"],
            padx=18,
            pady=18
        )

        card.pack(
            fill=tk.BOTH,
            expand=True,
            padx=22,
            pady=(0, 15)
        )

        tk.Label(
            card,
            text="Default target folder",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor=tk.W
        )

        entry = tk.Entry(
            card,
            textvariable=self.selected_dir,
            bg=c["surface_2"],
            fg=c["text"],
            insertbackground=c["text"],
            relief=tk.FLAT,
            font=("Segoe UI", 10)
        )

        entry.pack(
            fill=tk.X,
            pady=(7, 4),
            ipady=7
        )

        ttk.Button(
            card,
            text="Browse...",
            command=self.browse_folder
        ).pack(
            anchor=tk.E
        )

        # ----------------------------------------------------
        # Options
        # ----------------------------------------------------

        tk.Label(
            card,
            text="Organizer options",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor=tk.W,
            pady=(18, 7)
        )

        settings_options = [
            (
                "Preserve folder structure",
                self.preserve_structure
            ),
            (
                "Dry run — no changes",
                self.dry_run
            ),
            (
                "Include hidden files",
                self.include_hidden
            ),
            (
                "Detect duplicates using hash",
                self.compute_duplicates
            )
        ]

        for text, variable in settings_options:

            tk.Checkbutton(
                card,
                text=text,
                variable=variable,
                bg=c["surface"],
                fg=c["text"],
                activebackground=c["surface"],
                activeforeground=c["text"],
                selectcolor=c["surface_2"],
                font=("Segoe UI", 9),
                anchor="w"
            ).pack(
                fill=tk.X,
                pady=2
            )

        # ----------------------------------------------------
        # File types
        # ----------------------------------------------------

        tk.Label(
            card,
            text="File type filter",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor=tk.W,
            pady=(12, 3)
        )

        tk.Entry(
            card,
            textvariable=self.include_suffixes,
            bg=c["surface_2"],
            fg=c["text"],
            insertbackground=c["text"],
            relief=tk.FLAT,
            font=("Segoe UI", 9)
        ).pack(
            fill=tk.X,
            ipady=6
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        buttons = tk.Frame(
            win,
            bg=c["background"]
        )

        buttons.pack(
            fill=tk.X,
            padx=22,
            pady=(0, 20)
        )

        def save_and_close():

            self._save_settings()

            win.destroy()

        ttk.Button(
            buttons,
            text="Reset Setup",
            command=lambda: reset_setup(),
            style="Small.TButton"
        ).pack(
            side=tk.LEFT
        )

        ttk.Button(
            buttons,
            text="Cancel",
            command=win.destroy,
            style="Small.TButton"
        ).pack(
            side=tk.RIGHT,
            padx=5
        )

        ttk.Button(
            buttons,
            text="Save",
            command=save_and_close,
            style="Primary.TButton"
        ).pack(
            side=tk.RIGHT
        )

        # ----------------------------------------------------
        # Reset
        # ----------------------------------------------------

        def reset_setup():

            confirm = messagebox.askyesno(
                "Reset Settings",
                "Reset all settings to defaults?\n\n"
                "This will remove organizer_settings.json."
            )

            if not confirm:
                return

            try:

                if SETTINGS_FILE.exists():
                    SETTINGS_FILE.unlink()

                self.selected_dir.set("")
                self.preserve_structure.set(True)
                self.dry_run.set(False)
                self.include_hidden.set(False)
                self.compute_duplicates.set(False)
                self.include_suffixes.set("")

                self.current_theme = "dark"

                if tb:

                    try:

                        self.style.theme_use(
                            "darkly"
                        )

                    except Exception:
                        pass

                self._configure_styles()
                self._apply_theme_adjustments()

                self._save_settings(
                    auto=True
                )

                self._enqueue_log(
                    "✓ Settings reset to defaults."
                )

                self.refresh_preview()

                messagebox.showinfo(
                    "Reset",
                    "Settings have been reset."
                )

            except Exception as e:

                messagebox.showerror(
                    "Reset failed",
                    str(e)
                )

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        if self.observer:

            try:

                self.observer.stop()
                self.observer.join(
                    timeout=1
                )

            except Exception:
                pass

            self.observer = None


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Root
    # --------------------------------------------------------

    if Window:

        root = Window(
            themename="darkly",
            title="Smart File Organizer",
            size=(1180, 850)
        )

    else:

        root = tk.Tk()

        root.title(
            "Smart File Organizer"
        )

        root.geometry(
            "1180x850"
        )

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    app = SmartOrganizerApp(
        root
    )

    # --------------------------------------------------------
    # Close handler
    # --------------------------------------------------------

    def on_close():

        app.close()

        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        on_close
    )

    root.mainloop()