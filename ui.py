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
from PIL import Image, ImageTk, ImageDraw, ImageFont

from file_sorter import sort_directory, undo, redo

# watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # חלון ללא גבולות
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 10))
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ------------------------ Logger ------------------------
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

# ------------------------ DPI Awareness ------------------------
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ------------------------ File Icon Helper ------------------------
FILE_ICONS = {}

FILE_TYPE_COLORS = {
    ".txt": (135,206,250,255),     # תכלת
    ".py": (255,223,0,255),        # צהוב
    ".jpg": (255,160,122,255),     # כתום
    ".png": (144,238,144,255),     # ירוק בהיר
    ".pdf": (220,20,60,255),       # אדום
    ".mp3": (255,105,180,255),     # ורוד
    ".mp4": (255,140,0,255),       # כתום כהה
}

def get_file_icon(file_path: Path, size=(48,48)):
    """
    מחזיר תמונה קטנה (thumbnail) של הקובץ או תיקיה.
    תיקיות מקבלות אייקון כחול עם DIR.
    קבצים מקבלים צבע לפי סוג.
    """
    suffix = file_path.suffix.lower()
    key = ("DIR" if file_path.is_dir() else suffix)

    if key in FILE_ICONS:
        return FILE_ICONS[key]

    img = Image.new("RGBA", size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    if file_path.is_dir():
        # תיקיה כחולה
        draw.rectangle([4, 12, size[0]-4, size[1]-4], fill=(70,130,180,255))
        draw.rectangle([4,4,size[0]//2,12], fill=(100,149,237,255))
        txt = "DIR"
        bbox = draw.textbbox((0,0), txt, font=font)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
        draw.text(((size[0]-w)/2,(size[1]-h)/2), txt, fill="white", font=font)
    else:
        color = FILE_TYPE_COLORS.get(suffix, (180,180,180,255))
        draw.rectangle([0,0,size[0],size[1]], fill=color)
        txt = suffix[1:].upper() if suffix else "FILE"
        bbox = draw.textbbox((0,0), txt, font=font)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
        draw.text(((size[0]-w)/2,(size[1]-h)/2), txt, fill="black", font=font)

        # אם תמונה, השתמש ב-thumbnail עם border אחיד
        if suffix in [".png",".jpg",".jpeg",".gif",".bmp"]:
            try:
                im = Image.open(file_path).convert("RGBA")
                im.thumbnail(size, Image.LANCZOS)

                # צור תמונה ריבועית בגודל אחיד
                thumb = Image.new("RGBA", size, (0,0,0,0))
                # חשב מיקום מרכזי
                x = (size[0] - im.width) // 2
                y = (size[1] - im.height) // 2
                thumb.paste(im, (x, y))
                FILE_ICONS[key] = thumb
                return thumb
            except:
                pass

    FILE_ICONS[key] = img
    return img

# ------------------------ Watchdog Handler ------------------------
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        self.callback()

# ------------------------ App ------------------------
class SmartOrganizerApp:
    THUMB_SIZE = (48,48)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("980x800")
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
        self.include_suffixes = tk.StringVar(value="")
        self.progress_value = tk.IntVar(value=0)

        self.log_queue = queue.Queue()
        self.preview_images = []

        self.observer = None

        self._build_ui()
        self._load_settings()
        self.root.after(200, self._process_log_queue)
        # התצוגה תתרענן אוטומטית כשמשנים גודל חלון
        self.canvas.bind("<Configure>", lambda e: self._on_canvas_resize())

    # ------------------ UI ------------------
    def _build_ui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f5f7fa")
        style.configure("TLabel", background="#f5f7fa", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=6)
        style.configure("TCheckbutton", background="#f5f7fa", font=("Segoe UI", 11))

        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(frm, text="🧠 Smart File Organizer", font=("Segoe UI", 20, "bold"))
        title.pack(pady=(0,8))

        # Directory
        dir_frame = ttk.Frame(frm)
        dir_frame.pack(fill=tk.X, pady=4)
        ttk.Label(dir_frame, text="Target Folder:").pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_dir, font=("Segoe UI", 12))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)

        # Options
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

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill=tk.X, pady=8)
        self.sort_btn = ttk.Button(btn_frame, text="▶ Sort Files", command=self.on_sort)
        self.sort_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 Open Folder", command=self.open_folder).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="⤺ Undo", command=self.on_undo).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="↻ Redo", command=self.on_redo).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Save Settings", command=self._save_settings).pack(side=tk.RIGHT)

        # Progress & stats
        self.progress = ttk.Progressbar(frm, mode="determinate", variable=self.progress_value, maximum=100)
        self.progress.pack(fill=tk.X, pady=(8,6))
        self.status_label = ttk.Label(frm, text="Ready", anchor="w", font=("Segoe UI", 10, "italic"))
        self.status_label.pack(fill=tk.X)
        stats_frame = ttk.Frame(frm)
        stats_frame.pack(fill=tk.X, pady=(4,8))
        self.stats_label = ttk.Label(stats_frame, text="Files: 0 | Moved: 0 | Duplicates: 0")
        self.stats_label.pack(side=tk.LEFT)

        # Log output
        self.output = scrolledtext.ScrolledText(frm, height=8, bg="#1e1e1e", fg="#dcdcdc", font=("Consolas", 11))
        self.output.pack(fill=tk.BOTH, expand=False, pady=(4,6))

        # Preview canvas
        self.preview_frame = ttk.Frame(frm)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.preview_frame, bg="#ffffff")
        self.scrollbar = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw", width=self.canvas.winfo_width())
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _schedule_refresh(self):
        # אם כבר מתוזמן רענון קודם, בטל אותו
        if hasattr(self, "_refresh_after_id"):
            try:
                self.root.after_cancel(self._refresh_after_id)
            except:
                pass
        # קבע רענון חדש אחרי 400 מילישניות
        self._refresh_after_id = self.root.after(400, self.refresh_preview)

    # ------------------ Folder ------------------
    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_dir.set(path)
            self.refresh_preview()
            self.start_watchdog()

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

    # ------------------ Sort ------------------
    def on_sort(self):
        folder = self.selected_dir.get()
        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return
        self.sort_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Scanning files...", foreground="#0066cc")
        self.progress_value.set(0)
        thread = threading.Thread(target=self._sort_worker, args=(folder,), daemon=True)
        thread.start()

    def _sort_worker(self, folder):
        dest_root = Path(folder)
        suffix_filter = [s.strip().lower() for s in self.include_suffixes.get().split(",") if s.strip()]
        self._enqueue_log(f"Starting sorting: {folder}")
        def progress_cb(processed,total):
            pct = int((processed/total)*100) if total else 100
            self.root.after(0, lambda: self._update_progress(pct))
            self.root.after(0, self.refresh_preview)
        try:
            summary = sort_directory(
                root_dir=Path(folder),
                dest_root=dest_root,
                preserve_structure=self.preserve_structure.get(),
                dry_run=self.dry_run.get(),
                include_hidden=self.include_hidden.get(),
                exclude_patterns=None,
                min_size_bytes=0,
                max_size_bytes=None,
                compute_duplicates=self.compute_duplicates.get(),
                progress_callback=progress_cb,
                suffix_filter=suffix_filter
            )
            moved = summary["moved_count"]
            total = summary["total_files"]
            duration = summary.get("duration_seconds",0.0)
            dup = summary.get("duplicate_count",0)
            self._enqueue_log(f"✅ Done. Scanned: {total}, Moved: {moved}, Duplicates: {dup}, Time: {duration:.2f}s")
            for src,dst,moved_flag in summary["moved_items"][:80]:
                self._enqueue_log(f"{'MOVED' if moved_flag else '[DRY]'}: {src} → {dst}")
            if len(summary["moved_items"])>80:
                self._enqueue_log(f"... and {len(summary['moved_items'])-80} more entries")
            self.root.after(0, lambda: self._update_stats(total,moved,dup))
        except Exception as e:
            logger.exception("Error during sorting")
            self._enqueue_log(f"❌ Error: {e}")
        finally:
            self.root.after(0, self._finish_sort)

    # ------------------ Preview ------------------
    def refresh_preview(self):
        folder = self.selected_dir.get()
        if not folder or not Path(folder).exists():
            return

        # נקה את התצוגה הקודמת
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.preview_images.clear()

        items = list(Path(folder).iterdir())

        # קבע את הגודל של כל cell (ריבוע אחיד)
        canvas_width = max(self.canvas.winfo_width(), 400)
        cell_size = 80  # כולל padding
        cols = max(1, canvas_width // cell_size)

        for idx, item in enumerate(items):
            frame = ttk.Frame(self.inner_frame, width=cell_size, height=cell_size, relief=tk.RIDGE, borderwidth=1)
            frame.grid_propagate(False)  # מונע שה-frame ישנה את הגודל לפי תוכן
            row = idx // cols
            col = idx % cols
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            thumb_img = get_file_icon(item, size=self.THUMB_SIZE)
            thumb = ImageTk.PhotoImage(thumb_img)
            lbl = ttk.Label(frame, image=thumb)
            lbl.image = thumb
            lbl.pack(pady=2)

            ToolTip(lbl, text=item.name)

            # שם הקובץ, מוגבל לשורה אחת עם … אם ארוך מדי
            name = item.name
            if len(name) > 12:
                name = name[:10] + "…"
            name_lbl = ttk.Label(frame, text=name, wraplength=cell_size-10, justify="center")
            name_lbl.pack(side=tk.BOTTOM, pady=2)

            self.preview_images.append(thumb)

        # הגדרת משקל לכל עמודה כדי למלא את השורה
        for c in range(cols):
            self.inner_frame.columnconfigure(c, weight=1)

        # עדכון אזור הגלילה
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def _on_canvas_resize(self, event=None):
        """מתאים את רוחב ה-inner_frame לגודל הקנבס ומרענן"""
        try:
            self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
        except:
            pass

        # ביטול הטיימר הקודם רק אם באמת קיים
        if hasattr(self, "_resize_after_id"):
            try:
                self.root.after_cancel(self._resize_after_id)
            except:
                pass
            
        # הפעלת טיימר חדש לעדכון
        self._resize_after_id = self.root.after(300, self.refresh_preview)

    # ------------------ Watchdog ------------------
    def start_watchdog(self):
        if hasattr(self, "observer") and self.observer:
            self.observer.stop()
            self.observer.join()

        folder = self.selected_dir.get()
        if not folder:
            return
        
        event_handler = FolderChangeHandler(lambda: self._schedule_refresh())
        self.observer = Observer()
        self.observer.schedule(event_handler, folder, recursive=False)
        self.observer.start()

    # ------------------ Logging ------------------
    def _enqueue_log(self,msg):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_queue.put(f"{timestamp} {msg}")

    def _process_log_queue(self):
        while True:
            try:
                line = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.output.insert(tk.END,line+"\n")
            self.output.see(tk.END)
        self.root.after(200,self._process_log_queue)

    # ------------------ Undo/Redo ------------------
    def on_undo(self):
        folder = self.selected_dir.get()
        if not folder:
            messagebox.showwarning("No folder","Please select a folder first.")
            return
        confirm = messagebox.askyesno("Undo Last","Are you sure you want to undo the last sort operation?")
        if not confirm:
            return
        self._enqueue_log("Attempting undo of last operation...")
        thread = threading.Thread(target=self._undo_worker,args=(Path(folder),),daemon=True)
        thread.start()

    def _undo_worker(self,dest_root:Path):
        try:
            result = undo(dest_root)
            if result.get("errors"):
                for e in result["errors"]:
                    self._enqueue_log(f"UNDO ERROR: {e}")
            self._enqueue_log(f"Undone moves: {result.get('undone',0)}")
            if result.get("removed_dirs"):
                for d in result["removed_dirs"]:
                    self._enqueue_log(f"Removed empty dir: {d}")
            self.root.after(0, lambda:self._update_stats(0,0,0))
            self.root.after(0, self.refresh_preview)
        except Exception as e:
            logger.exception("Undo error")
            self._enqueue_log(f"Undo failed: {e}")

    def on_redo(self):
        folder = self.selected_dir.get()
        if not folder:
            messagebox.showwarning("No folder","Please select a folder first.")
            return
        self._enqueue_log("Attempting redo of next operation...")
        thread = threading.Thread(target=self._redo_worker,args=(Path(folder),),daemon=True)
        thread.start()

    def _redo_worker(self,dest_root:Path):
        try:
            result = redo(dest_root)
            if result.get("errors"):
                for e in result["errors"]:
                    self._enqueue_log(f"REDO ERROR: {e}")
            self._enqueue_log(f"Redone moves: {result.get('redone',0)}")
            if result.get("created_dirs"):
                for d in result["created_dirs"]:
                    self._enqueue_log(f"Re-created dir: {d}")
            self.root.after(0, lambda:self._update_stats(0,0,0))
            self.root.after(0, self.refresh_preview)
        except Exception as e:
            logger.exception("Redo error")
            self._enqueue_log(f"Redo failed: {e}")

    # ------------------ Misc ------------------
    def clear_log(self):
        self.output.delete("1.0", tk.END)

    def _update_stats(self,total,moved,dup):
        self.stats_label.config(text=f"Files: {total} | Moved: {moved} | Duplicates: {dup}")

    def _save_settings(self):
        data = {
            "last_folder": self.selected_dir.get(),
            "preserve_structure": self.preserve_structure.get(),
            "dry_run": self.dry_run.get(),
            "include_hidden": self.include_hidden.get(),
            "compute_duplicates": self.compute_duplicates.get(),
            "include_suffixes": self.include_suffixes.get()
        }
        try:
            with SETTINGS_FILE.open("w",encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            self._enqueue_log("Settings saved.")
        except Exception as e:
            self._enqueue_log(f"Failed to save settings: {e}")

    def _load_settings(self):
        if not SETTINGS_FILE.exists():
            return
        try:
            with SETTINGS_FILE.open("r",encoding="utf-8") as fh:
                data = json.load(fh)
            self.selected_dir.set(data.get("last_folder",""))
            self.preserve_structure.set(data.get("preserve_structure",True))
            self.dry_run.set(data.get("dry_run",False))
            self.include_hidden.set(data.get("include_hidden",False))
            self.compute_duplicates.set(data.get("compute_duplicates",False))
            self.include_suffixes.set(data.get("include_suffixes",""))
            self._enqueue_log("Settings loaded.")
            self.refresh_preview()
            if self.selected_dir.get():
                self.start_watchdog()
        except Exception as e:
            self._enqueue_log(f"Failed to load settings: {e}")

    # ------------------ Progress ------------------
    def _update_progress(self,pct):
        self.progress_value.set(pct)
        self.status_label.config(text=f"Progress: {pct}%")

    def _finish_sort(self):
        self.progress_value.set(100)
        self.sort_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Done ✅", foreground="green")
        self.root.after(900, lambda:self.progress_value.set(0))
        self.refresh_preview()

# ------------------ Main ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartOrganizerApp(root)

    def on_close():
        if hasattr(app, "observer") and app.observer:
            app.observer.stop()
            app.observer.join()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
