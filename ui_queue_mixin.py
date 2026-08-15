"""
UIQueueMixin: the single, central mechanism through which ANY
background thread (sort worker, undo/redo worker, watchdog observer
thread) safely requests a UI update.

Why this exists:
Tkinter widgets/variables must only be touched from the main thread.
Calling `self.root.after(...)` *from a background thread* is commonly
assumed to be safe (it's an extremely common pattern in tutorials),
but it is not reliably safe -- in testing it caused
"RuntimeError: main thread is not in main loop" and, worse, silently
dropped updates so the UI got stuck (progress bar frozen, button
never re-enabled) even though the underlying work had completed.

This affected three independent places in the original code:
  - the sort worker thread (progress/stats/completion)
  - the undo/redo worker threads (stats/preview refresh)
  - the watchdog observer thread (live preview refresh on any
    filesystem change -- the app's core "live monitoring" feature)

The fix: background threads only ever push plain data into a
`queue.Queue` (which *is* thread-safe). A single poller, scheduled
exclusively via `root.after()` from the main thread, drains it and
applies the updates. Multiple queued "refresh"/"progress" messages
between polls are coalesced into a single UI update, which also
naturally debounces rapid-fire watchdog events without needing any
cross-thread `after()`/`after_cancel()` calls.
"""

import queue

# How often the main thread checks the UI queue (ms).
UI_QUEUE_POLL_MS = 120


class UIQueueMixin:

    def _process_ui_queue(self):

        latest_progress = None
        latest_stats = None
        want_refresh = False
        sort_done = False

        while True:

            try:
                kind, payload = self.ui_queue.get_nowait()
            except queue.Empty:
                break

            if kind == "progress":
                latest_progress = payload

            elif kind == "stats":
                latest_stats = payload

            elif kind == "refresh":
                want_refresh = True

            elif kind == "sort_done":
                sort_done = True

        if latest_progress is not None:
            self._update_progress(latest_progress)

        if latest_stats is not None:
            self._update_stats(*latest_stats)

        if want_refresh:
            self.refresh_preview()

        if sort_done:
            self._finish_sort()
            self._resume_watchdog_after_sort()

        # Keep polling for the lifetime of the app.
        self.root.after(UI_QUEUE_POLL_MS, self._process_ui_queue)
