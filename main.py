import tkinter as tk
from ui import SmartOrganizerApp
import argparse
import sys
from pathlib import Path

def main_cli():
    parser = argparse.ArgumentParser(description="Smart File Organizer - CLI mode")
    parser.add_argument("folder", nargs="?", help="Folder to sort (optional; opens GUI if not provided)")
    parser.add_argument("--dry-run", action="store_true", help="Do not move files, only simulate")
    parser.add_argument("--no-gui", action="store_true", help="Run in CLI mode and exit")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files")
    parser.add_argument("--duplicates", action="store_true", help="Compute duplicates (hash)")
    args = parser.parse_args()

    if args.folder and args.no_gui:
        from file_sorter import sort_directory
        folder = Path(args.folder)
        if not folder.exists():
            print("Folder not found:", folder)
            sys.exit(1)
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

    # otherwise start GUI
    root = tk.Tk()
    app = SmartOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main_cli()
