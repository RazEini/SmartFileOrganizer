"""
FolderMixin: browsing for a target folder and opening it in the OS
file explorer.
"""

import os
import sys
from tkinter import filedialog, messagebox


class FolderMixin:

    def browse_folder(self):

        path = filedialog.askdirectory()

        if path:

            self.selected_dir.set(path)

            self.refresh_preview()
            self.start_watchdog()

            self._enqueue_log(f"Selected folder: {path}")
            self._save_settings(auto=True)

    def open_folder(self):

        path = self.selected_dir.get()

        if not path:
            messagebox.showwarning("No folder", "Please select a folder first.")
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
            messagebox.showerror("Open folder failed", str(e))
