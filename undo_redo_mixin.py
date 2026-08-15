"""
UndoRedoMixin: undo/redo of the last sort operation, run in
background threads.

Fix: these workers used to call `self.root.after(0, ...)` directly
from a background thread to push stats/preview updates. That is not
reliably thread-safe (see ui_queue_mixin.py). Now they push into the
shared, thread-safe ui_queue instead, which the main thread drains.
"""

import threading
from pathlib import Path
from tkinter import messagebox

from file_sorter import undo, redo
from logging_setup import logger


class UndoRedoMixin:

    # ========================================================
    # UNDO
    # ========================================================

    def on_undo(self):

        folder = self.selected_dir.get()

        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        confirm = messagebox.askyesno(
            "Undo Last Operation",
            "Are you sure you want to undo the last sort operation?"
        )

        if not confirm:
            return

        self._enqueue_log("↶ Attempting undo...")

        thread = threading.Thread(target=self._undo_worker, args=(Path(folder),), daemon=True)
        thread.start()

    def _undo_worker(self, dest_root: Path):

        try:

            result = undo(dest_root)

            if result.get("errors"):
                for error in result["errors"]:
                    self._enqueue_log(f"UNDO ERROR: {error}")

            self._enqueue_log(f"✓ Undone moves: {result.get('undone', 0)}")

            if result.get("removed_dirs"):
                for directory in result["removed_dirs"]:
                    self._enqueue_log(f"Removed empty dir: {directory}")

            self.ui_queue.put(("stats", (0, 0, 0)))
            self.ui_queue.put(("refresh", None))

        except Exception as e:

            logger.exception("Undo error")
            self._enqueue_log(f"Undo failed: {e}")

    # ========================================================
    # REDO
    # ========================================================

    def on_redo(self):

        folder = self.selected_dir.get()

        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        self._enqueue_log("↷ Attempting redo...")

        thread = threading.Thread(target=self._redo_worker, args=(Path(folder),), daemon=True)
        thread.start()

    def _redo_worker(self, dest_root: Path):

        try:

            result = redo(dest_root)

            if result.get("errors"):
                for error in result["errors"]:
                    self._enqueue_log(f"REDO ERROR: {error}")

            self._enqueue_log(f"✓ Redone moves: {result.get('redone', 0)}")

            if result.get("created_dirs"):
                for directory in result["created_dirs"]:
                    self._enqueue_log(f"Re-created dir: {directory}")

            self.ui_queue.put(("stats", (0, 0, 0)))
            self.ui_queue.put(("refresh", None))

        except Exception as e:

            logger.exception("Redo error")
            self._enqueue_log(f"Redo failed: {e}")
