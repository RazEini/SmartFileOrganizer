import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
import threading
import time
import logging
import os
import sys
import queue
import json
from logging.handlers import RotatingFileHandler

from file_sorter import sort_directory, undo, redo

# ------------------------
# Logger setup (integrated)
# ------------------------
LOG_FILE = Path("sorted_files_log.txt")

def setup_logger(level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger("smart_organizer")
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(message)s"))

    fh = RotatingFileHandler(str(LOG_FILE), maxBytes=5_000_000, backupCount=5, encoding="utf-8", mode='a')
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))

    logger.handlers = []
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False
    return logger

logger = setup_logger()

SETTINGS_FILE = Path("organizer_settings.json")

# ------------------------
# DPI Awareness for Windows
# ------------------------
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class SmartOrganizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("980x700")
        self.root.configure(bg="#f5f7fa")

        try:
            self.root.tk.call('tk', 'scaling', 1.5)
        except Exception:
            pass

        # Variables
        self.selected_dir = tk.StringVar()
        self.preserve_structure = tk.BooleanVar(value=True)
        self.dry_run = tk.BooleanVar(value=False)
        self.include_hidden = tk.BooleanVar(value=False)
        self.compute_duplicates = tk.BooleanVar(value=False)
        self.include_suffixes = tk.StringVar(value="")  # החדש
        self.progress_value = tk.IntVar(value=0)
        self.total_files = 0

        self.log_queue = queue.Queue()

        self._build_ui()
        self._load_settings()
        self.root.after(200, self._process_log_queue)

    def _build_ui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f5f7fa")
        style.configure("TLabel", background="#f5f7fa", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=6)
        style.configure("TCheckbutton", background="#f5f7fa", font=("Segoe UI", 11))

        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(frm, text="🧠 Smart File Organizer", font=("Segoe UI", 20, "bold"))
        title.pack(pady=(0, 8))

        dir_frame = ttk.Frame(frm)
        dir_frame.pack(fill=tk.X, pady=4)
        ttk.Label(dir_frame, text="Target Folder:").pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_dir, font=("Segoe UI", 12))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)

        opts_frame = ttk.Frame(frm)
        opts_frame.pack(fill=tk.X, pady=6)

        left = ttk.Frame(opts_frame)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Checkbutton(left, text="Preserve folder structure", variable=self.preserve_structure).pack(anchor=tk.W, padx=2, pady=2)
        ttk.Checkbutton(left, text="Dry run (no changes)", variable=self.dry_run).pack(anchor=tk.W, padx=2, pady=2)
        ttk.Checkbutton(left, text="Include hidden files", variable=self.include_hidden).pack(anchor=tk.W, padx=2, pady=2)
        ttk.Checkbutton(left, text="Detect duplicates (hash)", variable=self.compute_duplicates).pack(anchor=tk.W, padx=2, pady=2)

        right = ttk.Frame(opts_frame)
        right.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20,0))
        ttk.Label(right, text="Include only file types (e.g. .png,.jpg,.pdf):").pack(anchor=tk.W, pady=(6,0))
        ttk.Entry(right, textvariable=self.include_suffixes).pack(fill=tk.X, pady=2)

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill=tk.X, pady=8)
        self.sort_btn = ttk.Button(btn_frame, text="▶ Sort Files", command=self.on_sort)
        self.sort_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 Open Folder", command=self.open_folder).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="⤺ Undo", command=self.on_undo).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="↻ Redo", command=self.on_redo).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Save Settings", command=self._save_settings).pack(side=tk.RIGHT)

        # Progress and stats
        self.progress = ttk.Progressbar(frm, mode="determinate", variable=self.progress_value, maximum=100)
        self.progress.pack(fill=tk.X, pady=(8, 6))
        self.status_label = ttk.Label(frm, text="Ready", anchor="w", font=("Segoe UI", 10, "italic"))
        self.status_label.pack(fill=tk.X)

        stats_frame = ttk.Frame(frm)
        stats_frame.pack(fill=tk.X, pady=(4, 8))
        self.stats_label = ttk.Label(stats_frame, text="Files: 0 | Moved: 0 | Duplicates: 0")
        self.stats_label.pack(side=tk.LEFT)

        self.output = scrolledtext.ScrolledText(frm, height=20, bg="#1e1e1e", fg="#dcdcdc", font=("Consolas", 11))
        self.output.pack(fill=tk.BOTH, expand=True, pady=(4, 6))

    # --- Folder browse/open ---
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

    # --- Sort logic ---
    def on_sort(self):
        folder = self.selected_dir.get()
        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        self.sort_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Scanning files...", foreground="#0066cc")
        self.progress.config(mode="determinate")
        self.progress_value.set(0)

        thread = threading.Thread(target=self._sort_worker, args=(folder,), daemon=True)
        thread.start()

    def _sort_worker(self, folder):
        dest_root = Path(folder)
        suffix_filter = [s.strip().lower() for s in self.include_suffixes.get().split(",") if s.strip()]

        self._enqueue_log(f"Starting sorting: {folder}")

        def progress_cb(processed, total):
            pct = int((processed / total) * 100) if total else 100
            self.root.after(0, lambda: self._update_progress(pct))

        try:
            summary = sort_directory(
                root_dir=Path(folder),
                dest_root=dest_root,
                preserve_structure=self.preserve_structure.get(),
                dry_run=self.dry_run.get(),
                include_hidden=self.include_hidden.get(),
                exclude_patterns=None,  # לא נדרש
                min_size_bytes=0,
                max_size_bytes=None,
                compute_duplicates=self.compute_duplicates.get(),
                progress_callback=progress_cb,
                suffix_filter=suffix_filter  # חדש
            )
            moved = summary["moved_count"]
            total = summary["total_files"]
            duration = summary.get("duration_seconds", 0.0)
            dup = summary.get("duplicate_count", 0)
            self._enqueue_log(f"✅ Done. Scanned: {total}, Moved: {moved}, Duplicates: {dup}, Time: {duration:.2f}s")
            for src, dst, moved_flag in summary["moved_items"][:80]:
                self._enqueue_log(f"{'MOVED' if moved_flag else '[DRY]'}: {src} → {dst}")
            if len(summary["moved_items"]) > 80:
                self._enqueue_log(f"... and {len(summary['moved_items']) - 80} more entries")
            self.root.after(0, lambda: self._update_stats(total, moved, dup))
        except Exception as e:
            logger.exception("Error during sorting")
            self._enqueue_log(f"❌ Error: {e}")
        finally:
            self.root.after(0, self._finish_sort)

    def _update_progress(self, pct: int):
        self.progress_value.set(pct)
        self.status_label.config(text=f"Progress: {pct}%")

    def _finish_sort(self):
        self.progress_value.set(100)
        self.sort_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Done ✅", foreground="green")
        self.root.after(900, lambda: self.progress_value.set(0))

    # --- Logging ---
    def _enqueue_log(self, msg: str):
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

    # --- Undo/Redo ---
    def on_undo(self):
        folder = self.selected_dir.get()
        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return
        confirm = messagebox.askyesno("Undo Last", "Are you sure you want to undo the last sort operation?")
        if not confirm:
            return
        self._enqueue_log("Attempting undo of last operation...")
        thread = threading.Thread(target=self._undo_worker, args=(Path(folder),), daemon=True)
        thread.start()

    def _undo_worker(self, dest_root: Path):
        try:
            result = undo(dest_root)
            if result.get("errors"):
                for e in result["errors"]:
                    self._enqueue_log(f"UNDO ERROR: {e}")
            self._enqueue_log(f"Undone moves: {result.get('undone', 0)}")
            if result.get("removed_dirs"):
                for d in result["removed_dirs"]:
                    self._enqueue_log(f"Removed empty dir: {d}")
            self.root.after(0, lambda: self._update_stats(0, 0, 0))
        except Exception as e:
            logger.exception("Undo error")
            self._enqueue_log(f"Undo failed: {e}")

    def on_redo(self):
        folder = self.selected_dir.get()
        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return
        self._enqueue_log("Attempting redo of next operation...")
        thread = threading.Thread(target=self._redo_worker, args=(Path(folder),), daemon=True)
        thread.start()

    def _redo_worker(self, dest_root: Path):
        try:
            result = redo(dest_root)
            if result.get("errors"):
                for e in result["errors"]:
                    self._enqueue_log(f"REDO ERROR: {e}")
            self._enqueue_log(f"Redone moves: {result.get('redone', 0)}")
            if result.get("created_dirs"):
                for d in result["created_dirs"]:
                    self._enqueue_log(f"Re-created dir: {d}")
            self.root.after(0, lambda: self._update_stats(0, 0, 0))
        except Exception as e:
            logger.exception("Redo error")
            self._enqueue_log(f"Redo failed: {e}")

    # --- Misc ---
    def clear_log(self):
        self.output.delete("1.0", tk.END)

    def _update_stats(self, total: int, moved: int, dup: int):
        self.stats_label.config(text=f"Files: {total} | Moved: {moved} | Duplicates: {dup}")

    def _save_settings(self):
        data = {
            "last_folder": self.selected_dir.get(),
            "preserve_structure": self.preserve_structure.get(),
            "dry_run": self.dry_run.get(),
            "include_hidden": self.include_hidden.get(),
            "compute_duplicates": self.compute_duplicates.get(),
            "include_suffixes": self.include_suffixes.get()  # החדש
        }
        try:
            with SETTINGS_FILE.open("w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            self._enqueue_log("Settings saved.")
        except Exception as e:
            self._enqueue_log(f"Failed to save settings: {e}")

    def _load_settings(self):
        if not SETTINGS_FILE.exists():
            return
        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.selected_dir.set(data.get("last_folder", ""))
            self.preserve_structure.set(data.get("preserve_structure", True))
            self.dry_run.set(data.get("dry_run", False))
            self.include_hidden.set(data.get("include_hidden", False))
            self.compute_duplicates.set(data.get("compute_duplicates", False))
            self.include_suffixes.set(data.get("include_suffixes", ""))  # החדש
            self._enqueue_log("Settings loaded.")
        except Exception as e:
            self._enqueue_log(f"Failed to load settings: {e}")
