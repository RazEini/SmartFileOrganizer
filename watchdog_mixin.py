"""
WatchdogMixin: starts/stops filesystem monitoring of the selected
folder to trigger live preview refreshes.

Fix: the watchdog observer runs its own background thread, and its
event callback used to call `self.root.after(...)` /
`self.root.after_cancel(...)` directly -- i.e. every single
filesystem change (the app's core "live monitoring" feature) made an
unsafe cross-thread Tk call. This could raise
"RuntimeError: main thread is not in main loop" or silently drop the
refresh.

Now the callback just pushes a ("refresh", None) message into the
shared, thread-safe ui_queue. The queue poller (ui_queue_mixin.py)
already coalesces multiple refresh requests received between polls
into a single refresh_preview() call, so rapid bursts of filesystem
events (e.g. a sort operation, or copying many files in) still only
cause one UI refresh per poll cycle -- no debounce timer needed.
"""

from watchdog.observers import Observer
from watchdog_handler import FolderChangeHandler


class WatchdogMixin:

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

        event_handler = FolderChangeHandler(self._on_folder_changed)

        self.observer = Observer()

        try:

            self.observer.schedule(event_handler, folder, recursive=False)
            self.observer.start()

            self._enqueue_log("● Live folder monitoring enabled.")

        except Exception as e:
            self._enqueue_log(f"Watchdog failed to start: {e}")

    def _on_folder_changed(self):
        # Called from the watchdog observer's own background thread --
        # must only touch the thread-safe queue, never a Tk widget or
        # `self.root.after(...)` directly.
        self.ui_queue.put(("refresh", None))
