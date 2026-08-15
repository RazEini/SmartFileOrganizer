"""
Simple hover tooltip widget used for file names in the preview grid.
"""

import tkinter as tk


class ToolTip:

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):

        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)

        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#111827",
            foreground="#f8fafc",
            relief=tk.FLAT,
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        label.pack(ipadx=8, ipady=5)

    def hide_tip(self, event=None):

        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
