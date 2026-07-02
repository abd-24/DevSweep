"""
services/recycle_service.py

Responsible for moving files and directories to the OS recycle bin. 
No permanent deletion, files are recoverable for safety purpose.
"""

from pathlib import Path
from send2trash import send2trash, TrashPermissionError

def delete(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    if path.is_symlink():
        raise ValueError(f"Refusing to delete symlink: {path}")
    try:
        send2trash(str(path))
    except TrashPermissionError as e:
        raise PermissionError(f"Permission denied: {path}") from e
    except OSError as e:
        raise OSError(f"Failed to delete {path}") from e