# Smart File Organizer

A simple desktop tool to organize files by type into category folders.
Built with Python and Tkinter. No external APIs required.

## Features
- Sort files into categories (Images, Documents, Code, Videos, etc.)
- Option to preserve folder structure when moving files
- Dry-run option to preview changes without moving files
- GUI (Tkinter) with activity log
- Collision-safe filename resolution (adds " (1)" if name exists)
- Logging to sorted_files_log.txt

## Requirements
- Python 3.8+
- Uses only standard library modules (no pip installs required)

## Run
1. Clone repository or copy files.
2. `python main.py`
3. Select a folder, choose options, and click "Sort Files".

## Notes
- Always test with `Dry run` enabled first.
- The app avoids moving files that are already in the destination tree.
- Edit `FILE_CATEGORIES` in `file_sorter.py` to add/remove file type mappings.
