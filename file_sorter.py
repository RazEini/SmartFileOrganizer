from pathlib import Path
import shutil
import logging
from typing import Dict, List, Tuple, Optional, Callable
import hashlib
import json
import time

logger = logging.getLogger("smart_organizer")

# Default category mapping — extend as you like
FILE_CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".odt", ".rtf"],
    "Code": [".py", ".java", ".cpp", ".c", ".h", ".js", ".html", ".css", ".ts", ".go", ".rb"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
    "Audio": [".mp3", ".wav", ".aac", ".ogg", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Spreadsheets": [".xls", ".xlsx", ".csv"],
    "Presentations": [".ppt", ".pptx"]
}

UNKNOWN_CATEGORY = "Others"
HISTORY_FILE = ".sort_history.json"  # stored under dest_root

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

def compute_file_hash(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    """
    Compute SHA256 hash in streaming fashion (chunked) — suitable for large files.
    Returns empty string on error.
    """
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
    except Exception as e:
        logger.debug("Error hashing %s: %s", path, e)
        return ""
    return h.hexdigest()

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

def _should_skip(path: Path, root_dir: Path, dest_root: Path, include_hidden: bool, exclude_patterns: Optional[List[str]] = None) -> bool:
    if not include_hidden and any(part.startswith(".") for part in path.parts):
        return True
    # skip files already under category folders
    for category in FILE_CATEGORIES.keys():
        try:
            if path.is_relative_to(dest_root / category):
                return True
        except Exception:
            pass
    # exclude by pattern
    if exclude_patterns:
        for pat in exclude_patterns:
            if path.match(pat):
                return True
    return False

def _remove_empty_dirs(paths: List[Path]) -> List[Path]:
    """
    Attempt to remove directories in 'paths' if they are empty (and contain no new files).
    Returns list of removed dirs (strings).
    """
    removed = []
    for d in sorted(paths, key=lambda p: len(str(p)), reverse=True):  # remove deeper first
        try:
            if d.exists() and d.is_dir():
                # consider directory empty if no files and no non-empty subdirs
                is_empty = True
                for _ in d.rglob("*"):
                    is_empty = False
                    break
                if is_empty:
                    d.rmdir()
                    removed.append(d)
        except Exception as e:
            logger.debug("Failed to remove dir %s: %s", d, e)
    return removed

def sort_directory(
    root_dir: Path,
    dest_root: Optional[Path] = None,
    preserve_structure: bool = True,
    dry_run: bool = False,
    include_hidden: bool = False,
    exclude_patterns: Optional[List[str]] = None,
    min_size_bytes: int = 0,
    max_size_bytes: Optional[int] = None,
    compute_duplicates: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> dict:
    """
    Sort files under root_dir into category folders placed in dest_root (defaults to root_dir).
    progress_callback(current, total) may be called to update UI progress.
    Returns summary dict with counts, moved items, created_dirs list etc.
    """
    if dest_root is None:
        dest_root = root_dir

    root_dir = root_dir.resolve()
    dest_root = dest_root.resolve()

    summary = {
        "root": str(root_dir),
        "dest_root": str(dest_root),
        "total_files": 0,
        "moved_count": 0,
        "moved_items": [],  # list of tuples (src, dst, moved_bool)
        "duplicate_count": 0,
        "duration_seconds": 0.0,
        "created_dirs": []  # directories created during this operation
    }

    start_time = time.time()

    # Gather files first (determine total for progress)
    files: List[Path] = []
    hashes = {}
    # Simple single pass file gathering (we don't pre-hash all; only if compute_duplicates)
    for p in root_dir.rglob("*"):
        if p.is_dir():
            continue
        if _should_skip(p, root_dir, dest_root, include_hidden, exclude_patterns):
            continue
        try:
            size = p.stat().st_size
        except Exception:
            continue
        if min_size_bytes and size < min_size_bytes:
            continue
        if max_size_bytes and size > max_size_bytes:
            continue
        files.append(p)

    total = len(files)
    summary["total_files"] = total

    # If duplicates requested, compute hashes for files grouped by size first (efficiency)
    if compute_duplicates:
        size_map = {}
        for p in files:
            try:
                s = p.stat().st_size
            except Exception:
                continue
            size_map.setdefault(s, []).append(p)
        # only hash groups with more than 1 item
        for size, group in size_map.items():
            if len(group) > 1:
                for p in group:
                    h = compute_file_hash(p)
                    if not h:
                        continue
                    hashes.setdefault(h, []).append(p)
        # Note: files with unique sizes won't appear in hashes; duplicates variable below uses hashes

    # process files with progress updates
    processed = 0
    created_dirs_set = set()

    for p in files:
        suffix = p.suffix.lower()
        category = find_category_for_suffix(suffix)
        category_dir = dest_root / category

        if preserve_structure:
            try:
                rel = p.relative_to(root_dir)
            except Exception:
                rel = Path(p.name)
            if rel.parent == Path("."):
                dst = category_dir / p.name
            else:
                dst = category_dir / rel.parent / p.name
        else:
            dst = category_dir / p.name

        # If duplicates detection active and file hash is in hashes with >1 entries
        moved = False
        if compute_duplicates:
            h = compute_file_hash(p)
            if h and h in hashes and len(hashes[h]) > 1:
                duplicates_dir = dest_root / "Duplicates" / category
                if preserve_structure:
                    try:
                        rel = p.relative_to(root_dir)
                    except Exception:
                        rel = Path(p.name)
                    if rel.parent == Path("."):
                        dst = duplicates_dir / p.name
                    else:
                        dst = duplicates_dir / rel.parent / p.name
                else:
                    dst = duplicates_dir / p.name
                final_dst, moved = move_file(p, dst, dry_run=dry_run)
                # record created dirs
                created_dirs_set.add(str(Path(final_dst).parent))
                summary["moved_items"].append((str(p), str(final_dst), moved))
                if moved:
                    summary["moved_count"] += 1
                    summary["duplicate_count"] += 1
            else:
                final_dst, moved = move_file(p, dst, dry_run=dry_run)
                created_dirs_set.add(str(Path(final_dst).parent))
                summary["moved_items"].append((str(p), str(final_dst), moved))
                if moved:
                    summary["moved_count"] += 1
        else:
            final_dst, moved = move_file(p, dst, dry_run=dry_run)
            created_dirs_set.add(str(Path(final_dst).parent))
            summary["moved_items"].append((str(p), str(final_dst), moved))
            if moved:
                summary["moved_count"] += 1

        processed += 1
        if progress_callback:
            try:
                progress_callback(processed, total)
            except Exception:
                pass

    summary["created_dirs"] = sorted(list(set(created_dirs_set)))

    # write history with pointer for undo/redo
    history_entry = {
        "timestamp": time.time(),
        "root": str(root_dir),
        "dest_root": str(dest_root),
        "items": [{"src": s, "dst": d, "moved": m} for (s, d, m) in summary["moved_items"]],
        "created_dirs": summary["created_dirs"]
    }

    try:
        hist_path = dest_root / HISTORY_FILE
        existing = {"pointer": -1, "entries": []}
        if hist_path.exists():
            try:
                with hist_path.open("r", encoding="utf-8") as fh:
                    existing = json.load(fh)
            except Exception:
                existing = {"pointer": -1, "entries": []}
        # if we undid some operations before, drop redo-able entries
        pointer = existing.get("pointer", -1)
        entries = existing.get("entries", [])
        # truncate to pointer+1
        entries = entries[: pointer + 1] if pointer + 1 <= len(entries) else entries
        entries.append(history_entry)
        pointer = len(entries) - 1
        new_hist = {"pointer": pointer, "entries": entries}
        if not dry_run:
            with hist_path.open("w", encoding="utf-8") as fh:
                json.dump(new_hist, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.debug("Failed to write history: %s", e)

    # duration
    summary["duration_seconds"] = time.time() - start_time
    return summary

def undo(dest_root: Path) -> dict:
    """
    Undo last operation (if any). Returns summary with undone count and removed_dirs list.
    This also removes empty created_dirs recorded in the undone entry (but only if still empty).
    """
    hist_path = dest_root / HISTORY_FILE
    result = {"undone": 0, "errors": [], "removed_dirs": [], "redo_available": False}
    if not hist_path.exists():
        result["errors"].append("No history file found.")
        return result
    try:
        with hist_path.open("r", encoding="utf-8") as fh:
            state = json.load(fh)
    except Exception as e:
        result["errors"].append(f"Failed to read history: {e}")
        return result

    pointer = state.get("pointer", -1)
    entries = state.get("entries", [])
    if pointer < 0 or pointer >= len(entries):
        result["errors"].append("No operation to undo.")
        return result

    last = entries[pointer]
    # move items back in reverse order
    for item in reversed(last.get("items", [])):
        src = Path(item["dst"])
        dst = Path(item["src"])
        try:
            if src.exists():
                ensure_dir(dst.parent)
                shutil.move(str(src), str(dst))
                result["undone"] += 1
            else:
                result["errors"].append(f"Source not found for undo: {src}")
        except Exception as e:
            result["errors"].append(f"Error moving {src} -> {dst}: {e}")

    # attempt to remove empty created_dirs from this entry
    created_dirs = [Path(p) for p in last.get("created_dirs", [])]
    removed = _remove_empty_dirs(created_dirs)
    result["removed_dirs"] = [str(p) for p in removed]

    # move pointer back (so redo becomes available)
    state["pointer"] = pointer - 1
    try:
        with hist_path.open("w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        result["errors"].append(f"Failed to update history: {e}")

    result["redo_available"] = True
    return result

def redo(dest_root: Path) -> dict:
    """
    Redo the next operation if available. Re-applies the operation at pointer+1.
    """
    hist_path = dest_root / HISTORY_FILE
    result = {"redone": 0, "errors": [], "created_dirs": []}
    if not hist_path.exists():
        result["errors"].append("No history file found.")
        return result
    try:
        with hist_path.open("r", encoding="utf-8") as fh:
            state = json.load(fh)
    except Exception as e:
        result["errors"].append(f"Failed to read history: {e}")
        return result

    pointer = state.get("pointer", -1)
    entries = state.get("entries", [])
    next_idx = pointer + 1
    if next_idx < 0 or next_idx >= len(entries):
        result["errors"].append("No operation to redo.")
        return result

    entry = entries[next_idx]
    # reapply moves in original order
    for item in entry.get("items", []):
        src = Path(item["src"])
        dst = Path(item["dst"])
        try:
            if src.exists():
                ensure_dir(dst.parent)
                shutil.move(str(src), str(dst))
                result["redone"] += 1
            else:
                # if original src doesn't exist, maybe it was moved; try to continue
                result["errors"].append(f"Redo source missing: {src}")
        except Exception as e:
            result["errors"].append(f"Error moving {src} -> {dst}: {e}")

    # update pointer
    state["pointer"] = next_idx
    try:
        with hist_path.open("w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        result["errors"].append(f"Failed to update history: {e}")

    result["created_dirs"] = entry.get("created_dirs", [])
    return result
