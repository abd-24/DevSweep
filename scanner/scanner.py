# Responsible for recursively walking the directory tree
# Collects all folders and files under a given root.

from pathlib import Path
from dataclasses import dataclass, field
import os


@dataclass
class ScanResult:
    """
    The raw output of a scan.
    Just counts and paths — nothing interpreted yet.
    """
    root: Path
    folders: list[Path] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)

    @property
    def folder_count(self) -> int:
        return len(self.folders)

    @property
    def file_count(self) -> int:
        return len(self.files)

    def summary(self) -> str:
        return (
            f"Scanned: {self.root}\n"
            f"  Folders : {self.folder_count}\n"
            f"  Files   : {self.file_count}"
        )

# Level 1 — never descend, ever
ALWAYS_SKIP = {
    ".git",
    ".idea",
    ".vscode",
    "reports",
}

def scan(root: Path, skip_hidden: bool = True, skip_deletables: set = None) -> ScanResult:
    """
    Recursively walk every folder and file under root.

    Args:
        root:        The directory to scan.
        skip_hidden: If True, skips folders/files starting with '.'
                     (e.g. .git, .venv). Recommended for most scans.

    Returns:
        A ScanResult containing every folder and file found.

    Raises:
        ValueError: If root does not exist or is not a directory.
    """
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    result = ScanResult(root=root)

    # os.walk yields (current_dir, subdirs, files) where current_dir is a string
    for current_dir, subdirs, files in os.walk(root):
        current_dir = Path(current_dir)

        # Record deletable folders at this level (they're not descended into)
        for d in list(subdirs):
            folder_path = current_dir / d
            try:
                if folder_path.is_symlink():
                    continue
            except OSError:
                continue

            if skip_deletables and d in skip_deletables:
                result.folders.append(folder_path)

        # Mutate subdirs in-place to control which directories os.walk descends into
        subdirs[:] = [
            d for d in subdirs
            if d not in ALWAYS_SKIP
            and not (skip_hidden and d.startswith("."))
            and (skip_deletables is None or d not in skip_deletables)
        ]

        for d in subdirs:
            folder_path = current_dir / d

            # skip symbolic links — follow-through can cause infinite loops
            try:
                if folder_path.is_symlink():
                    continue
            except OSError:
                continue

            result.folders.append(folder_path)

        for filename in files:
            file_path = current_dir / filename

            if skip_hidden and filename.startswith("."):
                continue

            try:
                if file_path.is_symlink():
                    continue
            except OSError:
                continue

            result.files.append(file_path)

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scanner.py <path>")
        sys.exit(1)

    target = Path(sys.argv[1])

    try:
        result = scan(target)
        print(result.summary())
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
