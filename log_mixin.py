"""
LogMixin: thread-safe activity log queue and its periodic flush into
the ScrolledText widget.
"""

import time
import tkinter as tk
import queue


class LogMixin:

    def _enqueue_log(self, msg):

        timestamp = time.strftime("[%H:%M:%S]")
        self.log_queue.put(f"{timestamp} {msg}")

    def _process_log_queue(self):

        while True:

            try:
                line = self.log_queue.get_nowait()
            except queue.Empty:
                break

            self.output.insert(tk.END, line + "\n")
            self.output.see(tk.END)

        self.root.after(200, self._process_log_queue)

    def clear_log(self):
        self.output.delete("1.0", tk.END)
