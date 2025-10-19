# ui.py (HiDPI / Modern) - Updated
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
import threading
import time
import logging
import os
import sys

from file_sorter import sort_directory
from logger import setup_logger

logger = setup_logger()

# ------------------------
# DPI Awareness for Windows
# ------------------------
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1=System DPI aware
except Exception:
    pass  # Non-Windows systems ignore

class SmartOrganizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("800x550")
        self.root.configure(bg="#f5f7fa")

        # ------------------------
        # Global scaling for HiDPI
        # ------------------------
        self.root.tk.call('tk', 'scaling', 1.5)

        # ------------------------
        # Variables
        # ------------------------
        self.selected_dir = tk.StringVar()
        self.preserve_structure = tk.BooleanVar(value=True)
        self.dry_run = tk.BooleanVar(value=False)
        self.include_hidden = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f5f7fa")
        style.configure("TLabel", background="#f5f7fa", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=6)
        style.configure("TCheckbutton", background="#f5f7fa", font=("Segoe UI", 11))

        frm = ttk.Frame(self.root, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(frm, text="🧠 Smart File Organizer", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(0, 10))

        # Folder selection
        dir_frame = ttk.Frame(frm)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dir_frame, text="Target Folder:").pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_dir, font=("Segoe UI", 12))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)

        # Options
        opts_frame = ttk.Frame(frm)
        opts_frame.pack(fill=tk.X, pady=10)
        ttk.Checkbutton(opts_frame, text="Preserve folder structure", variable=self.preserve_structure).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(opts_frame, text="Dry run (no changes)", variable=self.dry_run).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(opts_frame, text="Include hidden files", variable=self.include_hidden).pack(side=tk.LEFT, padx=5)

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill=tk.X, pady=10)
        self.sort_btn = ttk.Button(btn_frame, text="▶ Sort Files", command=self.on_sort)
        self.sort_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 Open Folder", command=self.open_folder).pack(side=tk.LEFT)

        # Progress Bar
        self.progress = ttk.Progressbar(frm, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(5, 10))

        # Output log
        ttk.Label(frm, text="Activity Log:").pack(anchor=tk.W)
        self.output = scrolledtext.ScrolledText(frm, height=18, bg="#1e1e1e", fg="#dcdcdc", font=("Consolas", 11))
        self.output.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Status bar
        self.status_label = ttk.Label(frm, text="Ready", anchor="w", font=("Segoe UI", 10, "italic"))
        self.status_label.pack(fill=tk.X, pady=(2, 0))

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_dir.set(path)

    def open_folder(self):
        path = self.selected_dir.get()
        if not path:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return
        try:
            os.startfile(path)
        except Exception:
            import subprocess
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

    def on_sort(self):
        folder = self.selected_dir.get()
        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        self.sort_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Sorting...", foreground="#0066cc")
        self.progress.start(10)

        thread = threading.Thread(target=self._sort_worker, args=(folder,), daemon=True)
        thread.start()

    def _sort_worker(self, folder):
        start = time.time()
        self._log(f"Starting sorting: {folder}")
        try:
            # ⚡ Use a separate "_sorted" folder to avoid recursive moves
            dest_root = Path(folder) / "_sorted"
            summary = sort_directory(
                root_dir=Path(folder),
                dest_root=dest_root,
                preserve_structure=self.preserve_structure.get(),
                dry_run=self.dry_run.get(),
                include_hidden=self.include_hidden.get()
            )
            moved = summary["moved_count"]
            total = summary["total_files"]
            elapsed = time.time() - start
            self._log(f"✅ Done. Total files: {total}, Moved: {moved}, Time: {elapsed:.2f}s")
            for src, dst, moved_flag in summary["moved_items"][:30]:
                self._log(f"{'MOVED' if moved_flag else '[DRY]'}: {src} → {dst}")
        except Exception as e:
            logger.exception("Error during sorting")
            self._log(f"❌ Error: {e}")
        finally:
            self.root.after(0, self._finish_sort)

    def _finish_sort(self):
        self.progress.stop()
        self.sort_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Done ✅", foreground="green")

    def _log(self, msg: str):
        timestamp = time.strftime("[%H:%M:%S]")
        line = f"{timestamp} {msg}\n"
        self.output.insert(tk.END, line)
        self.output.see(tk.END)
        logger.info(msg)
