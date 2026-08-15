"""
SortMixin: runs the sort operation in a background thread and
reports progress/results back to the UI thread through the shared,
thread-safe ui_queue (see ui_queue_mixin.py for why this matters).

Additional fixes:
1. Threading safety (Variable reads): all tkinter Variable reads
   (preserve_structure, dry_run, include_hidden, compute_duplicates,
   include_suffixes) used to happen *inside* the background worker
   thread. Tkinter variables must only be read from the main thread.
   All values are now read on the main thread inside on_sort() and
   passed into the worker as plain arguments.
2. Live-preview "shaking" during sort: files move in real time, so
   naive per-file refreshes reflow the grid constantly. Fixed by:
     - pausing the watchdog observer for the duration of the sort
       (it would just be reacting to the sort's own file moves)
     - throttling preview refresh *requests* to a few times per
       second (on top of the natural coalescing the shared UI
       queue poller already does)
"""

import threading
import time
from pathlib import Path
from tkinter import messagebox

from file_sorter import sort_directory
from logging_setup import logger

# Minimum time between live preview refresh *requests* while sorting
# (seconds). The shared UI queue poller also coalesces bursts, but
# this avoids flooding the queue with hundreds of requests.
PREVIEW_REFRESH_INTERVAL = 0.35


class SortMixin:

    def on_sort(self):

        folder = self.selected_dir.get()

        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        if not Path(folder).exists():
            messagebox.showerror("Folder not found", "The selected folder does not exist.")
            return

        self.sort_btn.config(state="disabled")

        self.status_label.config(
            text="Scanning files...",
            foreground=self._colors()["primary"]
        )

        self.progress_value.set(0)
        self.progress_percent.config(text="0%")
        self.stats_status.config(text="RUNNING")

        # Pause live folder monitoring while we sort — the sort itself
        # generates a flood of filesystem events that would otherwise
        # queue up extra refreshes on top of the ones we already do.
        self._watchdog_was_active = self.observer is not None

        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=1)
            except Exception:
                pass
            self.observer = None

        self._last_preview_refresh_ts = 0.0

        # Read every tkinter Variable on the MAIN thread before handing
        # off to the worker. Tkinter Variables must not be touched from
        # a background thread.
        options = {
            "preserve_structure": self.preserve_structure.get(),
            "dry_run": self.dry_run.get(),
            "include_hidden": self.include_hidden.get(),
            "compute_duplicates": self.compute_duplicates.get(),
            "suffix_filter": [
                s.strip().lower()
                for s in self.include_suffixes.get().split(",")
                if s.strip()
            ],
        }

        thread = threading.Thread(
            target=self._sort_worker,
            args=(folder, options),
            daemon=True
        )
        thread.start()

    def _sort_worker(self, folder, options):

        dest_root = Path(folder)

        self._enqueue_log(f"▶ Starting sorting: {folder}")

        def progress_cb(processed, total):

            pct = int((processed / total) * 100) if total else 100
            self.ui_queue.put(("progress", pct))

            now = time.monotonic()

            if now - self._last_preview_refresh_ts >= PREVIEW_REFRESH_INTERVAL:
                self._last_preview_refresh_ts = now
                self.ui_queue.put(("refresh", None))

        try:

            summary = sort_directory(
                root_dir=Path(folder),
                dest_root=dest_root,
                preserve_structure=options["preserve_structure"],
                dry_run=options["dry_run"],
                include_hidden=options["include_hidden"],
                exclude_patterns=None,
                min_size_bytes=0,
                max_size_bytes=None,
                compute_duplicates=options["compute_duplicates"],
                progress_callback=progress_cb,
                suffix_filter=options["suffix_filter"]
            )

            moved = summary["moved_count"]
            total = summary["total_files"]
            duration = summary.get("duration_seconds", 0.0)
            dup = summary.get("duplicate_count", 0)

            self._enqueue_log(
                f"✓ Done | Scanned: {total} | "
                f"Moved: {moved} | "
                f"Duplicates: {dup} | "
                f"Time: {duration:.2f}s"
            )

            for src, dst, moved_flag in summary["moved_items"][:80]:

                prefix = "MOVED" if moved_flag else "[DRY]"
                self._enqueue_log(f"{prefix}: {src} → {dst}")

            if len(summary["moved_items"]) > 80:
                self._enqueue_log(
                    f"... and {len(summary['moved_items']) - 80} more entries"
                )

            self.ui_queue.put(("stats", (total, moved, dup)))

        except Exception as e:

            logger.exception("Error during sorting")
            self._enqueue_log(f"✕ Error: {e}")

        finally:

            self.ui_queue.put(("sort_done", None))

    def _resume_watchdog_after_sort(self):

        if getattr(self, "_watchdog_was_active", False):
            self.start_watchdog()
