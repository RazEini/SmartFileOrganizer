"""
PreviewMixin: renders the live thumbnail grid of the selected folder
and handles canvas resizing/scroll region updates.

Fix: uses a widget pool instead of destroy()+recreate on every
refresh. Rebuilding hundreds/thousands of widgets from scratch on
every watchdog tick or progress update caused visible flicker on
large folders. Now existing slot frames are reused and only their
content (image/text/position) is updated; new slots are created
only when the folder grows, and unused slots are hidden (not
destroyed) when the folder shrinks.
"""

import tkinter as tk
from pathlib import Path
from PIL import ImageTk

from icons import get_file_icon
from tooltip import ToolTip
from logging_setup import logger


class PreviewMixin:

    # Safety cap so a folder with tens of thousands of files doesn't
    # freeze the UI. Increase if needed.
    MAX_PREVIEW_ITEMS = 400

    def refresh_preview(self):

        folder = self.selected_dir.get()

        if not folder or not Path(folder).exists():
            return

        try:

            if not hasattr(self, "_preview_slots"):
                self._preview_slots = []

            items = sorted(
                Path(folder).iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )

            truncated = len(items) > self.MAX_PREVIEW_ITEMS
            items = items[: self.MAX_PREVIEW_ITEMS]

            canvas_width = max(self.canvas.winfo_width(), 420)
            cell_width = 105
            cols = max(1, canvas_width // cell_width)

            c = self._colors()

            self.preview_images = getattr(self, "preview_images", [])
            new_image_refs = []

            for idx, item in enumerate(items):

                row = idx // cols
                col = idx % cols

                if idx < len(self._preview_slots):
                    slot = self._preview_slots[idx]
                else:
                    slot = self._create_preview_slot()
                    self._preview_slots.append(slot)

                self._update_preview_slot(slot, item, c)

                slot["frame"].grid(
                    row=row, column=col, padx=7, pady=7, sticky="n"
                )

                new_image_refs.append(slot["image_ref"])

            # Hide (don't destroy) any leftover slots from a previous,
            # larger folder.
            for idx in range(len(items), len(self._preview_slots)):
                self._preview_slots[idx]["frame"].grid_forget()

            self.preview_images = new_image_refs

            for c_index in range(cols):
                self.inner_frame.columnconfigure(c_index, weight=1)

            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            if truncated:
                logger.info(
                    "Preview truncated to first %d items (folder has more).",
                    self.MAX_PREVIEW_ITEMS
                )

        except Exception:
            logger.exception("Preview refresh failed")

    # ========================================================
    # SLOT POOL HELPERS
    # ========================================================

    def _create_preview_slot(self):

        c = self._colors()

        frame = tk.Frame(
            self.inner_frame,
            bg=c["surface_2"],
            width=95,
            height=95
        )
        frame.grid_propagate(False)

        lbl = tk.Label(
            frame,
            bg=c["surface_2"],
            cursor="hand2",
            borderwidth=0
        )
        lbl.pack(pady=(8, 3))

        name_lbl = tk.Label(
            frame,
            bg=c["surface_2"],
            fg=c["text"],
            font=("Segoe UI", 8),
            wraplength=88,
            justify="center"
        )
        name_lbl.pack(fill=tk.X, padx=4)

        tooltip = ToolTip(lbl, text="")

        slot = {
            "frame": frame,
            "label": lbl,
            "name_label": name_lbl,
            "tooltip": tooltip,
            "image_ref": None,
            "path": None,
        }

        def on_enter(event, s=slot):
            colors = self._colors()
            s["frame"].configure(bg=colors["surface_3"])
            s["label"].configure(bg=colors["surface_3"])
            s["name_label"].configure(bg=colors["surface_3"])

        def on_leave(event, s=slot):
            colors = self._colors()
            s["frame"].configure(bg=colors["surface_2"])
            s["label"].configure(bg=colors["surface_2"])
            s["name_label"].configure(bg=colors["surface_2"])

        for widget in (frame, lbl, name_lbl):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return slot

    def _update_preview_slot(self, slot, item, c):

        # Skip re-decoding the thumbnail if this slot already shows
        # the same path (common case: nothing changed for that item).
        if slot["path"] == item and slot["image_ref"] is not None:
            slot["frame"].configure(bg=c["surface_2"])
            slot["label"].configure(bg=c["surface_2"])
            slot["name_label"].configure(bg=c["surface_2"])
            return

        thumb_img = get_file_icon(item, size=self.THUMB_SIZE)
        thumb = ImageTk.PhotoImage(thumb_img)

        slot["label"].configure(image=thumb, bg=c["surface_2"])
        slot["label"].image = thumb
        slot["image_ref"] = thumb

        name = item.name
        if len(name) > 14:
            name = name[:12] + "…"

        slot["name_label"].configure(text=name, bg=c["surface_2"], fg=c["text"])
        slot["frame"].configure(bg=c["surface_2"])

        slot["tooltip"].text = item.name
        slot["path"] = item

    # ========================================================
    # CANVAS RESIZE
    # ========================================================

    def _on_canvas_resize(self, event=None):

        try:
            self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
        except Exception:
            pass

        if hasattr(self, "_resize_after_id"):
            try:
                self.root.after_cancel(self._resize_after_id)
            except Exception:
                pass

        self._resize_after_id = self.root.after(300, self.refresh_preview)
