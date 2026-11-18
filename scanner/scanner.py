# Responsible for recursively walking the directory tree
# Collects all folders and files under a given root.
import os
from pathlib import Path
from dataclasses import dataclass, field


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

def scan(
    root: Path,
    skip_hidden: bool = True,
    skip_deletables: set[str] | None = None
) -> ScanResult:
    """
    Iteratively scan a directory tree using os.scandir().

    Deletable directories are recorded as candidates but never traversed.
    Symlinks and inaccessible directories are skipped.
    """

    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    result = ScanResult(root=root)
    skip_deletables = skip_deletables or set()

    stack = [root]

    while stack:
        current = stack.pop()

        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    name = entry.name

                    # Skip symlinks
                    try:
                        if entry.is_symlink() or entry.is_junction():
                            continue

                        is_dir = entry.is_dir(follow_symlinks=False)

                    except OSError:
                        continue

                    # Skip permanently excluded directories
                    if is_dir and name in ALWAYS_SKIP:
                        continue

                    # Skip hidden entries                    
                    is_deletable = is_dir and name in skip_deletables

                    if skip_hidden and name.startswith(".") and not is_deletable:
                        continue

                    path = Path(entry.path)

                    if is_dir:
                        # Record deletable directories, but don't descend
                        if name in skip_deletables:
                            result.folders.append(path)
                            continue

                        result.folders.append(path)
                        stack.append(path)

                    else:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                result.files.append(path)
                        except OSError:
                            continue

        except (PermissionError, OSError):
            continue

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