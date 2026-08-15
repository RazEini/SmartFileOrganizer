"""
UIMixin: builds the entire main-window layout (header, folder card,
options/actions, stats, progress, log + preview, footer).
"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class UIMixin:

    def _build_ui(self):

        self._configure_styles()

        c = self._colors()

        self.main = ttk.Frame(self.root, style="App.TFrame", padding=18)
        self.main.pack(fill=tk.BOTH, expand=True)

        # ====================================================
        # HEADER
        # ====================================================

        header = ttk.Frame(self.main, style="App.TFrame")
        header.pack(fill=tk.X, pady=(0, 16))

        title_frame = ttk.Frame(header, style="App.TFrame")
        title_frame.pack(side=tk.LEFT)

        ttk.Label(
            title_frame,
            text="Smart File Organizer",
            style="Title.TLabel"
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text="Organize your files. Keep your workspace clean.",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W, pady=(2, 0))

        header_buttons = ttk.Frame(header, style="App.TFrame")
        header_buttons.pack(side=tk.RIGHT, pady=4)

        self.theme_btn = ttk.Button(
            header_buttons,
            text="☀  Light / Dark",
            command=self.toggle_theme,
            style="Small.TButton"
        )
        self.theme_btn.pack(side=tk.LEFT, padx=4)

        self.settings_btn = ttk.Button(
            header_buttons,
            text="⚙  Settings",
            command=self.open_settings_window,
            style="Small.TButton"
        )
        self.settings_btn.pack(side=tk.LEFT, padx=4)

        # ====================================================
        # FOLDER CARD
        # ====================================================

        folder_card = ttk.Frame(self.main, style="Card.TFrame", padding=16)
        folder_card.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            folder_card,
            text="TARGET FOLDER",
            style="Section.TLabel"
        ).pack(anchor=tk.W)

        folder_row = ttk.Frame(folder_card, style="Card.TFrame")
        folder_row.pack(fill=tk.X, pady=(8, 0))

        # Fix: use dedicated style instead of raw background=/foreground=
        # kwargs (ttk.Label mostly ignores those and falls back to the
        # theme's default TLabel style, which caused the dark leftover
        # square behind the icon in light mode).
        folder_icon = ttk.Label(
            folder_row,
            text="📁",
            style="FolderIcon.TLabel"
        )
        folder_icon.pack(side=tk.LEFT, padx=(0, 10))

        self.dir_entry = ttk.Entry(
            folder_row,
            textvariable=self.selected_dir,
            style="Modern.TEntry"
        )
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            folder_row,
            text="Browse",
            command=self.browse_folder,
            style="Action.TButton"
        ).pack(side=tk.LEFT, padx=(8, 0))

        # ====================================================
        # OPTIONS + ACTIONS
        # ====================================================

        middle = ttk.Frame(self.main, style="App.TFrame")
        middle.pack(fill=tk.X, pady=(0, 12))

        # ----------------------------------------------------
        # OPTIONS CARD
        # ----------------------------------------------------

        options_card = ttk.Frame(middle, style="Card.TFrame", padding=14)
        options_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        ttk.Label(
            options_card,
            text="OPTIONS",
            style="Section.TLabel"
        ).pack(anchor=tk.W, pady=(0, 8))

        options_grid = ttk.Frame(options_card, style="Card.TFrame")
        options_grid.pack(fill=tk.X)

        self._make_checkbutton(options_grid, "Preserve folder structure", self.preserve_structure, 0, 0)
        self._make_checkbutton(options_grid, "Dry run — preview only", self.dry_run, 0, 1)
        self._make_checkbutton(options_grid, "Include hidden files", self.include_hidden, 1, 0)
        self._make_checkbutton(options_grid, "Detect duplicates", self.compute_duplicates, 1, 1)

        ttk.Label(
            options_card,
            text="File types filter  •  .png, .jpg, .pdf",
            style="Muted.TLabel"
        ).pack(anchor=tk.W, pady=(12, 3))

        ttk.Entry(
            options_card,
            textvariable=self.include_suffixes,
            style="Modern.TEntry"
        ).pack(fill=tk.X)

        # ----------------------------------------------------
        # ACTION CARD
        # ----------------------------------------------------

        action_card = ttk.Frame(middle, style="Card.TFrame", padding=14)
        action_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        ttk.Label(
            action_card,
            text="ACTIONS",
            style="Section.TLabel"
        ).pack(anchor=tk.W, pady=(0, 8))

        self.sort_btn = ttk.Button(
            action_card,
            text="▶  SORT FILES",
            command=self.on_sort,
            style="Primary.TButton"
        )
        self.sort_btn.pack(fill=tk.X, pady=(0, 8))

        action_row = ttk.Frame(action_card, style="Card.TFrame")
        action_row.pack(fill=tk.X)

        ttk.Button(
            action_row, text="↶ Undo", command=self.on_undo, style="Small.TButton"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        ttk.Button(
            action_row, text="↷ Redo", command=self.on_redo, style="Small.TButton"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        ttk.Button(
            action_row, text="📂 Open", command=self.open_folder, style="Small.TButton"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        # ====================================================
        # STATS
        # ====================================================

        stats_frame = ttk.Frame(self.main, style="App.TFrame")
        stats_frame.pack(fill=tk.X, pady=(0, 12))

        self.stats_total = self._create_stat_card(stats_frame, "FILES SCANNED", "0", "📄")
        self.stats_moved = self._create_stat_card(stats_frame, "FILES MOVED", "0", "↗")
        self.stats_duplicates = self._create_stat_card(stats_frame, "DUPLICATES", "0", "♢")
        self.stats_status = self._create_stat_card(stats_frame, "STATUS", "READY", "●")

        # ====================================================
        # PROGRESS
        # ====================================================

        progress_card = ttk.Frame(self.main, style="Card.TFrame", padding=(14, 10))
        progress_card.pack(fill=tk.X, pady=(0, 12))

        progress_top = ttk.Frame(progress_card, style="Card.TFrame")
        progress_top.pack(fill=tk.X)

        ttk.Label(
            progress_top,
            text="ORGANIZATION PROGRESS",
            style="Section.TLabel"
        ).pack(side=tk.LEFT)

        self.progress_percent = ttk.Label(progress_top, text="0%", style="Muted.TLabel")
        self.progress_percent.pack(side=tk.RIGHT)

        self.progress = ttk.Progressbar(
            progress_card,
            mode="determinate",
            variable=self.progress_value,
            maximum=100,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X, pady=(7, 3))

        self.status_label = ttk.Label(
            progress_card,
            text="Ready — select a folder to begin.",
            style="Status.TLabel"
        )
        self.status_label.pack(anchor=tk.W)

        # ====================================================
        # LOWER AREA
        # ====================================================

        lower = ttk.Frame(self.main, style="App.TFrame")
        lower.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # LOG CARD
        # ----------------------------------------------------

        log_card = ttk.Frame(lower, style="Card.TFrame", padding=10)
        log_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, ipadx=2, padx=(0, 6))
        log_card.configure(width=420)

        log_header = ttk.Frame(log_card, style="Card.TFrame")
        log_header.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(log_header, text="ACTIVITY LOG", style="Section.TLabel").pack(side=tk.LEFT)

        ttk.Button(
            log_header, text="Clear", command=self.clear_log, style="Small.TButton"
        ).pack(side=tk.RIGHT)

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
        self.output.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # PREVIEW CARD
        # ----------------------------------------------------

        preview_card = ttk.Frame(lower, style="Card.TFrame", padding=10)
        preview_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        preview_header = ttk.Frame(preview_card, style="Card.TFrame")
        preview_header.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(preview_header, text="FOLDER PREVIEW", style="Section.TLabel").pack(side=tk.LEFT)
        ttk.Label(preview_header, text="Live", style="Muted.TLabel").pack(side=tk.RIGHT)

        self.preview_frame = ttk.Frame(preview_card, style="Inner.TFrame")
        self.preview_frame.pack(fill=tk.BOTH, expand=True)

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

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner_frame = ttk.Frame(self.canvas, style="Inner.TFrame")

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw",
            width=400
        )

        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # ====================================================
        # FOOTER
        # ====================================================

        footer = ttk.Frame(self.main, style="App.TFrame")
        footer.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(
            footer,
            text="Smart File Organizer  •  Automatic settings  •  Live folder monitoring",
            style="Subtitle.TLabel"
        ).pack(side=tk.LEFT)

        ttk.Button(
            footer,
            text="Save Settings",
            command=self._save_settings,
            style="Small.TButton"
        ).pack(side=tk.RIGHT)

        self._apply_theme_adjustments()

    # ========================================================
    # UI HELPERS
    # ========================================================

    def _make_checkbutton(self, parent, text, variable, row, column):

        cb = ttk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            style="Modern.TCheckbutton"
        )

        cb.grid(row=row, column=column, sticky="w", padx=(0, 18), pady=4)

    def _create_stat_card(self, parent, title, value, icon):

        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill=tk.X)

        # Fix: dedicated "Icon.TLabel" style instead of raw kwargs
        # (see theme_mixin.py comment for why this matters).
        ttk.Label(
            top,
            text=icon,
            style="Icon.TLabel"
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(top, text=title, style="StatsCaption.TLabel").pack(side=tk.LEFT)

        value_label = ttk.Label(card, text=value, style="Stats.TLabel")
        value_label.pack(anchor=tk.W, pady=(4, 0))

        return value_label
