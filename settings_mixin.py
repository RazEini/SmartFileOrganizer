"""
SettingsMixin: JSON persistence of user preferences (auto-save on
change), plus the "Settings" Toplevel window.
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import ttkbootstrap as tb
except Exception:
    tb = None

from logging_setup import SETTINGS_FILE


class SettingsMixin:

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
                var.trace_add("write", lambda *args: self._save_settings(auto=True))

        except Exception:
            pass

    # ========================================================
    # SAVE / LOAD
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

            with SETTINGS_FILE.open("w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)

            if not auto:
                self._enqueue_log("✓ Settings saved.")

        except Exception as e:
            self._enqueue_log(f"Failed to save settings: {e}")

    def _load_settings(self):

        if not SETTINGS_FILE.exists():
            return

        try:

            with SETTINGS_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)

            self.selected_dir.set(data.get("last_folder", ""))
            self.preserve_structure.set(data.get("preserve_structure", True))
            self.dry_run.set(data.get("dry_run", False))
            self.include_hidden.set(data.get("include_hidden", False))
            self.compute_duplicates.set(data.get("compute_duplicates", False))
            self.include_suffixes.set(data.get("include_suffixes", ""))

            theme = data.get("theme")

            if theme in ("dark", "light"):

                self.current_theme = theme

                if tb:

                    bootstrap_theme = "darkly" if theme == "dark" else "flatly"

                    try:
                        self.style.theme_use(bootstrap_theme)
                    except tk.TclError as e:
                        if "Duplicate element" not in str(e):
                            raise

            self._configure_styles()
            self._apply_theme_adjustments()

            self._enqueue_log("✓ Settings loaded.")

            self.refresh_preview()

            if self.selected_dir.get() and __import__("pathlib").Path(self.selected_dir.get()).exists():
                self.start_watchdog()

        except Exception as e:
            self._enqueue_log(f"Failed to load settings: {e}")

    # ========================================================
    # SETTINGS WINDOW
    # ========================================================

    def open_settings_window(self):

        win = tk.Toplevel(self.root)

        win.title("Smart Organizer — Settings")
        win.geometry("520x470")
        win.minsize(500, 450)
        win.transient(self.root)

        c = self._colors()

        win.configure(background=c["background"])

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = tk.Frame(win, bg=c["background"])
        header.pack(fill=tk.X, padx=22, pady=(20, 12))

        tk.Label(
            header,
            text="Settings",
            bg=c["background"],
            fg=c["text"],
            font=("Segoe UI", 20, "bold")
        ).pack(anchor=tk.W)

        tk.Label(
            header,
            text="Configure how Smart File Organizer behaves.",
            bg=c["background"],
            fg=c["muted"],
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(2, 0))

        # ----------------------------------------------------
        # Main card
        # ----------------------------------------------------

        card = tk.Frame(win, bg=c["surface"], padx=18, pady=18)
        card.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 15))

        tk.Label(
            card,
            text="Default target folder",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)

        entry = tk.Entry(
            card,
            textvariable=self.selected_dir,
            bg=c["surface_2"],
            fg=c["text"],
            insertbackground=c["text"],
            relief=tk.FLAT,
            font=("Segoe UI", 10)
        )

        entry.pack(fill=tk.X, pady=(7, 4), ipady=7)

        ttk.Button(card, text="Browse...", command=self.browse_folder).pack(anchor=tk.E)

        # ----------------------------------------------------
        # Options
        # ----------------------------------------------------

        tk.Label(
            card,
            text="Organizer options",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(18, 7))

        settings_options = [
            ("Preserve folder structure", self.preserve_structure),
            ("Dry run — no changes", self.dry_run),
            ("Include hidden files", self.include_hidden),
            ("Detect duplicates using hash", self.compute_duplicates)
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
            ).pack(fill=tk.X, pady=2)

        # ----------------------------------------------------
        # File types
        # ----------------------------------------------------

        tk.Label(
            card,
            text="File type filter",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(12, 3))

        tk.Entry(
            card,
            textvariable=self.include_suffixes,
            bg=c["surface_2"],
            fg=c["text"],
            insertbackground=c["text"],
            relief=tk.FLAT,
            font=("Segoe UI", 9)
        ).pack(fill=tk.X, ipady=6)

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        buttons = tk.Frame(win, bg=c["background"])
        buttons.pack(fill=tk.X, padx=22, pady=(0, 20))

        def save_and_close():
            self._save_settings()
            win.destroy()

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
                        self.style.theme_use("darkly")
                    except tk.TclError as e:
                        if "Duplicate element" not in str(e):
                            raise

                self._configure_styles()
                self._apply_theme_adjustments()

                self._save_settings(auto=True)

                self._enqueue_log("✓ Settings reset to defaults.")

                self.refresh_preview()

                messagebox.showinfo("Reset", "Settings have been reset.")

            except Exception as e:
                messagebox.showerror("Reset failed", str(e))

        ttk.Button(
            buttons, text="Reset Setup", command=reset_setup, style="Small.TButton"
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons, text="Cancel", command=win.destroy, style="Small.TButton"
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            buttons, text="Save", command=save_and_close, style="Primary.TButton"
        ).pack(side=tk.RIGHT)
