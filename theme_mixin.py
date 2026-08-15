"""
ThemeMixin: handles dark/light theme switching and all ttk style
configuration.

Fixes applied:
1. toggle_theme() now tolerates the ttkbootstrap "Duplicate element"
   TclError that can occur when switching themes back and forth
   (known ttkbootstrap issue — safe to ignore, styles still apply).
2. Icon labels (folder icon + stat card icons) now use dedicated
   ttk styles ("FolderIcon.TLabel" / "Icon.TLabel") instead of raw
   background=/foreground= kwargs, which ttk.Label mostly ignores.
   This was the cause of the dark leftover squares behind icons
   in light mode.
"""

import tkinter as tk
from tkinter import messagebox

from colors import COLORS
from logging_setup import logger

try:
    import ttkbootstrap as tb
except Exception:
    tb = None


class ThemeMixin:

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

                try:
                    self.style.theme_use(bootstrap_theme)
                except tk.TclError as e:
                    # Known ttkbootstrap issue: switching themes back
                    # and forth can raise "Duplicate element ... indicator"
                    # even though the theme is applied correctly at the
                    # Tk engine level. Safe to swallow and continue.
                    if "Duplicate element" not in str(e):
                        raise
                    logger.warning(
                        "Ignored benign ttkbootstrap theme-switch error: %s",
                        e
                    )

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

        style.configure("App.TFrame", background=c["background"])
        style.configure("Card.TFrame", background=c["surface"])
        style.configure("Inner.TFrame", background=c["surface_2"])

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
        # Icon labels (fix: dedicated styles instead of raw kwargs)
        # ----------------------------------------------------

        style.configure(
            "FolderIcon.TLabel",
            background=c["surface"],
            foreground=c["text"],
            font=("Segoe UI Emoji", 22)
        )

        style.configure(
            "Icon.TLabel",
            background=c["surface"],
            foreground=c["primary"],
            font=("Segoe UI Emoji", 16)
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

            self.root.configure(background=c["background"])

            self.output.configure(
                bg=c["log_bg"],
                fg=c["log_fg"],
                insertbackground="#ffffff",
                selectbackground=c["primary"],
                selectforeground="#ffffff"
            )

            self.canvas.configure(bg=c["canvas"])

            self.preview_frame.configure(style="App.TFrame")
            self.inner_frame.configure(style="Inner.TFrame")

        except Exception:
            pass
