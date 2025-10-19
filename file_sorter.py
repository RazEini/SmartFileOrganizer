# file_sorter.py
from pathlib import Path
import shutil
import logging
from typing import Dict, List, Tuple

# Default category mapping — extend as you like
FILE_CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".odt"],
    "Code": [".py", ".java", ".cpp", ".c", ".h", ".js", ".html", ".css", ".ts", ".go", ".rb"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
    "Audio": [".mp3", ".wav", ".aac", ".ogg", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "PDFs": [".pdf"],
    "Spreadsheets": [".xls", ".xlsx", ".csv"],
    "Presentations": [".ppt", ".pptx"]
}

UNKNOWN_CATEGORY = "Others"

logger = logging.getLogger("file_sorter")


def find_category_for_suffix(suffix: str) -> str:
    suffix = suffix.lower()
    for category, exts in FILE_CATEGORIES.items():
        if suffix in exts:
            return category
    return UNKNOWN_CATEGORY


def ensure_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def unique_target_path(target: Path) -> Path:
    """
    If target exists, returns a new Path with a counter appended before suffix:
    example.txt -> example (1).txt
    """
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    i = 1
    while True:
        new_name = f"{stem} ({i}){suffix}"
        candidate = parent / new_name
        if not candidate.exists():
            return candidate
        i += 1


def move_file(src: Path, dst: Path, dry_run: bool = False) -> Tuple[Path, bool]:
    """
    Move a file from src to dst. Returns (final_dst, moved_bool).
    If dry_run True — don't actually move.
    """
    final_dst = unique_target_path(dst)
    if dry_run:
        logger.debug("[DRY-RUN] Would move %s -> %s", src, final_dst)
        return final_dst, False
    ensure_dir(final_dst.parent)
    shutil.move(str(src), str(final_dst))
    logger.info("moved: %s -> %s", src, final_dst)
    return final_dst, True


def sort_directory(
    root_dir: Path,
    dest_root: Path = None,
    preserve_structure: bool = True,
    dry_run: bool = False,
    include_hidden: bool = False
) -> dict:
    """
    Sort files under root_dir into category folders placed in dest_root (defaults to root_dir).
    preserve_structure: if True, maintain relative subpath under the category folder.
      e.g. root_dir/sub/f.txt -> root_dir/Images/sub/f.txt
    Returns summary dict with counts and moved items.
    """
    if dest_root is None:
        dest_root = root_dir

    summary = {
        "root": str(root_dir),
        "dest_root": str(dest_root),
        "total_files": 0,
        "moved_count": 0,
        "moved_items": []  # list of tuples (src, dst, moved_bool)
    }

    root_dir = root_dir.resolve()
    dest_root = dest_root.resolve()

    for p in root_dir.rglob("*"):
        # skip directories
        if p.is_dir():
            continue
        # skip files in dest_root if dest_root is inside root_dir to avoid relocating moved files
        if dest_root in p.parents and dest_root != root_dir:
            # don't process files that are already in destination tree (unless dest_root == root_dir)
            continue
        # optionally skip hidden files
        if not include_hidden and any(part.startswith(".") for part in p.parts):
            continue

        summary["total_files"] += 1
        suffix = p.suffix.lower()
        category = find_category_for_suffix(suffix)

        # Build destination path:
        category_dir = dest_root / category
        if preserve_structure:
            try:
                rel = p.relative_to(root_dir)
            except Exception:
                rel = p.name
            # place under category/<parent-of-file-relative-path>/
            if rel.parent == Path("."):
                dst = category_dir / p.name
            else:
                dst = category_dir / rel.parent / p.name
        else:
            dst = category_dir / p.name

        final_dst, moved = move_file(p, dst, dry_run=dry_run)
        summary["moved_items"].append((str(p), str(final_dst), moved))
        if moved:
            summary["moved_count"] += 1

    return summary
