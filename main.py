"""
Entry point for Smart File Organizer.

GUI mode:
    python main.py

CLI mode (no window, for automation / scripting):
    python main.py <folder> --no-gui [--dry-run] [--include-hidden] [--duplicates]
"""

import sys
import argparse
import tkinter as tk
from pathlib import Path

try:
    from ttkbootstrap import Window
except Exception:
    Window = None

# DPI awareness (Windows only)
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from app import SmartOrganizerApp
from file_sorter import sort_directory


def run_cli(args):

    folder = Path(args.folder)

    if not folder.exists():
        print("Folder not found:", folder)
        sys.exit(1)

    try:

        summary = sort_directory(
            root_dir=folder,
            dest_root=folder,
            preserve_structure=True,
            dry_run=args.dry_run,
            include_hidden=args.include_hidden,
            compute_duplicates=args.duplicates
        )

        print("Summary:")
        print(f"Total files scanned: {summary['total_files']}")
        print(f"Moved: {summary['moved_count']}")
        print(f"Duplicates found: {summary.get('duplicate_count', 0)}")

        sys.exit(0)

    except Exception as e:
        print("Error during sorting:", e)
        sys.exit(1)


def run_gui():

    if Window:
        root = Window(themename="darkly", title="Smart File Organizer", size=(1180, 850))
    else:
        root = tk.Tk()
        root.title("Smart File Organizer")
        root.geometry("1180x850")

    app = SmartOrganizerApp(root)

    def on_close():
        app.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


def main():

    if sys.version_info < (3, 9):
        print("Python 3.9+ is required.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Smart File Organizer")
    parser.add_argument("folder", nargs="?", help="Folder to sort (optional; opens GUI if not provided)")
    parser.add_argument("--dry-run", action="store_true", help="Do not move files, only simulate")
    parser.add_argument("--no-gui", action="store_true", help="Run in CLI mode and exit")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files")
    parser.add_argument("--duplicates", action="store_true", help="Compute duplicates (hash)")
    args = parser.parse_args()

    if args.folder and args.no_gui:
        run_cli(args)
        return

    run_gui()


if __name__ == "__main__":
    main()
