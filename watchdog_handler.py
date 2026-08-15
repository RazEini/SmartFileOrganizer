"""
Watchdog event handler used to detect folder changes for live preview.
"""

from watchdog.events import FileSystemEventHandler


class FolderChangeHandler(FileSystemEventHandler):

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        self.callback()
