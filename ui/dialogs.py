"""
ui/dialogs.py

Popup dialogs for confirmation, dry run preview, and error reporting.
"""

from pathlib import Path
from PySide6.QtWidgets import QMessageBox


def confirm_delete(parent, paths: list[Path], total_size: str) -> bool:
    result = QMessageBox.question(
        parent,
        "Confirm Deletion",
        f"Are you sure you want to delete {len(paths)} item(s)?\n\n"
        f"Total size: {total_size}\n\n"
        f"Items will be moved to the recycle bin.",
    )
    return result == QMessageBox.Yes


def show_dry_run(parent, paths: list[Path], sizes: dict[Path, str]):
    lines = ["Would delete:\n"]
    for path in paths:
        size = sizes.get(path, "?")
        lines.append(f"  {path.name}  —  {size}")
    lines.append(f"\nTotal: {sum_sizes(sizes, paths)}")
    lines.append("Nothing was deleted.")
    QMessageBox.information(parent, "Dry Run Preview", "\n".join(lines))


def sum_sizes(sizes: dict[Path, str], paths: list[Path]) -> str:
    # just show count for now, real size sum comes from file_service
    return f"{len(paths)} item(s)"


def show_error(parent, message: str):
    QMessageBox.critical(parent, "Error", message)