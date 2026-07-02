# File System operations.
"""
services/file_service.py

Responsible for calculating folder sizes and file counts.
"""
from pathlib import Path
def get_size(path: Path) -> int:
    """
    Calculate the total size of a file or directory in bytes.
    """
    if path.is_file():
        return path.stat().st_size
    if path.is_dir():
        total = 0
        for entry in path.rglob("*"):
            if entry.is_file() and not entry.is_symlink():
                try:
                    total += entry.stat().st_size
                except OSError:
                    continue
        return total
    return 0

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