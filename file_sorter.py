from pathlib import Path
import shutil
import hashlib
import time
import json
import logging
from typing import Optional, List, Callable, Dict, Tuple

logger = logging.getLogger("smart_organizer")

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
HISTORY_FILE = ".sort_history.json"

def find_category_for_suffix(suffix: str) -> str:
    suffix = suffix.lower()
    for cat, exts in FILE_CATEGORIES.items():
        if suffix in exts:
            return cat
    return UNKNOWN_CATEGORY

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def unique_target_path(target: Path) -> Path:
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    parent = target.parent
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def compute_file_hash(path: Path, chunk_size=8*1024*1024) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logger.debug("Hash error %s: %s", path, e)
        return ""

def move_file(src: Path, dst: Path, dry_run=False) -> Tuple[Path,bool]:
    final_dst = unique_target_path(dst)
    if dry_run:
        logger.debug("[DRY-RUN] %s -> %s", src, final_dst)
        return final_dst, False
    ensure_dir(final_dst.parent)
    shutil.move(str(src), str(final_dst))
    logger.info("Moved: %s -> %s", src, final_dst)
    return final_dst, True

def _should_skip(path: Path, root_dir: Path, dest_root: Path, include_hidden: bool, exclude_patterns: Optional[List[str]] = None) -> bool:
    if not include_hidden and any(part.startswith(".") for part in path.parts):
        return True
    for cat in FILE_CATEGORIES.keys():
        try:
            if path.is_relative_to(dest_root / cat):
                return True
        except Exception:
            pass
    if exclude_patterns:
        for pat in exclude_patterns:
            if path.match(pat):
                return True
    return False

def _remove_empty_dirs(paths: List[Path]) -> List[Path]:
    removed = []
    for d in sorted(paths, key=lambda p: len(str(p)), reverse=True):
        try:
            if d.exists() and d.is_dir() and not any(d.rglob("*")):
                d.rmdir()
                removed.append(d)
        except Exception as e:
            logger.debug("Remove dir fail %s: %s", d, e)
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
    progress_callback: Optional[Callable[[int,int],None]] = None,
    suffix_filter: Optional[List[str]] = None  # <-- אפשרות סינון לפי סיומות
) -> dict:
    if dest_root is None:
        dest_root = root_dir
    root_dir, dest_root = root_dir.resolve(), dest_root.resolve()
    summary = {"root": str(root_dir), "dest_root": str(dest_root), "total_files":0,
               "moved_count":0, "moved_items":[], "duplicate_count":0,
               "duration_seconds":0.0, "created_dirs":[]}
    start_time = time.time()
    files: List[Path] = []
    hashes = {}

    for p in root_dir.rglob("*"):
        if p.is_dir() or _should_skip(p, root_dir, dest_root, include_hidden, exclude_patterns):
            continue

        # סינון לפי סיומות אם נבחר
        if suffix_filter and p.suffix.lower() not in [s.lower() for s in suffix_filter]:
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
    summary["total_files"] = len(files)

    if compute_duplicates:
        size_map = {}
        for p in files:
            try:
                size = p.stat().st_size
            except Exception:
                continue
            size_map.setdefault(size, []).append(p)
        for group in size_map.values():
            if len(group) > 1:
                for p in group:
                    h = compute_file_hash(p)
                    if h:
                        hashes.setdefault(h, []).append(p)

    processed = 0
    created_dirs_set = set()
    for p in files:
        suffix = p.suffix.lower()
        category = find_category_for_suffix(suffix)
        category_dir = dest_root / category
        dst = category_dir / p.name
        if preserve_structure:
            try:
                rel = p.relative_to(root_dir)
                dst = category_dir / rel
            except Exception:
                dst = category_dir / p.name

        moved = False
        h = None
        if compute_duplicates:
            h = compute_file_hash(p)
            if h and len(hashes.get(h, [])) > 1:
                duplicates_dir = dest_root / "Duplicates" / category
                if preserve_structure:
                    try:
                        rel = p.relative_to(root_dir)
                        dst = duplicates_dir / rel
                    except Exception:
                        dst = duplicates_dir / p.name
                else:
                    dst = duplicates_dir / p.name
                final_dst, moved = move_file(p, dst, dry_run)
            else:
                final_dst, moved = move_file(p, dst, dry_run)
        else:
            final_dst, moved = move_file(p, dst, dry_run)

        created_dirs_set.add(str(final_dst.parent))
        summary["moved_items"].append((str(p), str(final_dst), moved))
        if moved:
            summary["moved_count"] += 1
            if compute_duplicates and h in hashes and len(hashes[h]) > 1:
                summary["duplicate_count"] += 1

        processed += 1
        if progress_callback:
            try:
                progress_callback(processed, len(files))
            except Exception:
                pass

    summary["created_dirs"] = sorted(list(created_dirs_set))
    summary["duration_seconds"] = time.time() - start_time

    # --- save history ---
    history_entry = {"timestamp":time.time(),"root":str(root_dir),"dest_root":str(dest_root),
                     "items":[{"src":s,"dst":d,"moved":m} for s,d,m in summary["moved_items"]],
                     "created_dirs":summary["created_dirs"]}
    try:
        hist_path = dest_root / HISTORY_FILE
        existing = {"pointer":-1,"entries":[]}
        if hist_path.exists():
            try:
                with hist_path.open("r", encoding="utf-8") as fh:
                    existing = json.load(fh)
            except Exception:
                existing = {"pointer":-1,"entries":[]}
        pointer = existing.get("pointer", -1)
        entries = existing.get("entries", [])
        entries = entries[:pointer+1] if pointer+1 <= len(entries) else entries
        entries.append(history_entry)
        pointer = len(entries)-1
        new_hist = {"pointer": pointer, "entries": entries}
        if not dry_run:
            with hist_path.open("w", encoding="utf-8") as fh:
                json.dump(new_hist, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.debug("Failed to write history: %s", e)
    return summary

# --- Undo / Redo functions נשארו ללא שינוי ---
def undo(dest_root: Path) -> dict:
    hist_path = dest_root / HISTORY_FILE
    result = {"undone":0,"errors":[],"removed_dirs":[],"redo_available":False}
    if not hist_path.exists():
        result["errors"].append("No history file found.")
        return result
    try:
        with hist_path.open("r",encoding="utf-8") as fh:
            state = json.load(fh)
    except Exception as e:
        result["errors"].append(f"Failed to read history: {e}")
        return result

    pointer = state.get("pointer",-1)
    entries = state.get("entries",[])
    if pointer<0 or pointer>=len(entries):
        result["errors"].append("No operation to undo.")
        return result

    last = entries[pointer]

    # --- Move files back to original locations ---
    for item in reversed(last.get("items",[])):
        src, dst = Path(item["dst"]), Path(item["src"])
        try:
            if src.exists():
                ensure_dir(dst.parent)
                shutil.move(str(src), str(dst))
                result["undone"] += 1
            else:
                result["errors"].append(f"Source not found for undo: {src}")
        except Exception as e:
            result["errors"].append(f"Error moving {src} -> {dst}: {e}")

    # --- Remove empty dirs created during this sort ---
    created_dirs = [Path(p) for p in last.get("created_dirs",[])]
    removed = _remove_empty_dirs(created_dirs)
    result["removed_dirs"].extend([str(p) for p in removed])

    # --- Remove empty Duplicates folder if it's now empty ---
    duplicates_root = dest_root / "Duplicates"
    if duplicates_root.exists():
        removed_dup = _remove_empty_dirs([duplicates_root])
        result["removed_dirs"].extend([str(p) for p in removed_dup])

    # --- Update history pointer ---
    state["pointer"] = pointer-1
    try:
        with hist_path.open("w",encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        result["errors"].append(f"Failed to update history: {e}")

    result["redo_available"] = True
    return result

def redo(dest_root: Path) -> dict:
    hist_path = dest_root / HISTORY_FILE
    result = {"redone":0,"errors":[],"created_dirs":[]}
    if not hist_path.exists():
        result["errors"].append("No history file found.")
        return result
    try:
        with hist_path.open("r",encoding="utf-8") as fh:
            state = json.load(fh)
    except Exception as e:
        result["errors"].append(f"Failed to read history: {e}")
        return result

    pointer = state.get("pointer",-1)
    entries = state.get("entries",[])
    next_idx = pointer + 1
    if next_idx < 0 or next_idx >= len(entries):
        result["errors"].append("No operation to redo.")
        return result

    entry = entries[next_idx]

    # --- Move files to their sorted locations ---
    for item in entry.get("items", []):
        src, dst = Path(item["src"]), Path(item["dst"])
        try:
            if src.exists():
                ensure_dir(dst.parent)
                shutil.move(str(src), str(dst))
                result["redone"] += 1
            else:
                if not dst.exists():
                    result["errors"].append(f"Redo source missing: {src}")
        except Exception as e:
            result["errors"].append(f"Error moving {src} -> {dst}: {e}")

    # --- Ensure all created dirs exist, including Duplicates ---
    created_dirs = [Path(p) for p in entry.get("created_dirs", [])]
    for d in created_dirs:
        ensure_dir(d)

    duplicates_root = dest_root / "Duplicates"
    if duplicates_root.exists():
        ensure_dir(duplicates_root)

    result["created_dirs"] = [str(d) for d in created_dirs]
    state["pointer"] = next_idx
    try:
        with hist_path.open("w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        result["errors"].append(f"Failed to update history: {e}")

    return result
