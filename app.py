"""
SmartOrganizerApp: composes all mixins into the final application
class. __init__ wires up state/vars and triggers the initial build.
"""

import tkinter as tk
import queue
from tkinter import ttk

try:
    import ttkbootstrap as tb
    from ttkbootstrap import Style
except Exception:
    tb = None
    Style = None

from theme_mixin import ThemeMixin
from ui_mixin import UIMixin
from folder_mixin import FolderMixin
from sort_mixin import SortMixin
from preview_mixin import PreviewMixin
from watchdog_mixin import WatchdogMixin
from log_mixin import LogMixin
from undo_redo_mixin import UndoRedoMixin
from stats_progress_mixin import StatsProgressMixin
from settings_mixin import SettingsMixin
from ui_queue_mixin import UIQueueMixin


class SmartOrganizerApp(
    ThemeMixin,
    UIMixin,
    FolderMixin,
    SortMixin,
    PreviewMixin,
    WatchdogMixin,
    LogMixin,
    UndoRedoMixin,
    StatsProgressMixin,
    SettingsMixin,
    UIQueueMixin,
):

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

        # log_queue: activity-log lines pushed from any background
        # thread, drained by _process_log_queue() on the main thread.
        self.log_queue = queue.Queue()

        # ui_queue: the single channel every background thread (sort
        # worker, undo/redo worker, watchdog observer thread) uses to
        # request UI updates. See ui_queue_mixin.py for why this is
        # required instead of calling `self.root.after(...)` directly
        # from those threads.
        self.ui_queue = queue.Queue()

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
        self.root.after(120, self._process_ui_queue)

        self.canvas.bind("<Configure>", self._on_canvas_resize)

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        if self.observer:

            try:
                self.observer.stop()
                self.observer.join(timeout=1)
            except Exception:
                pass

            self.observer = None
