# File System operations.
"""
services/file_service.py

Responsible for calculating folder sizes and file counts.
"""
import os
from pathlib import Path
def get_size(path: Path) -> int:
    """Total size in bytes of a file, or of everything inside a folder."""
    try:
        if path.is_file():
            return path.stat().st_size
    except OSError:
        return 0

    total = 0
    stack = [str(path)]

    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        if entry.is_symlink() or entry.is_junction():
                            continue                      # never follow links
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        else:
                            total += entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except OSError:
            continue

    return total

def get_file_count(path: Path) -> int:
    """
    Count the number of files in a directory or return 1 for a file.
    """
    if path.is_file():
        return 1
    if path.is_dir():
        return sum(
            1 for entry in path.rglob("*")
            if entry.is_file() and not entry.is_symlink()
        )
    return 0

def format_size(size_in_bytes: int) -> str:
    """
    Format the size in bytes into a human-readable string.
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f} TB"