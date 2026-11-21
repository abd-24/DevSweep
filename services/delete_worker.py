"""
services/delete_worker.py

Moves items to the recycle bin on a background thread so the UI stays responsive.
Like ScanWorker, it never touches widgets; it only emits signals.
"""

from pathlib import Path

from PySide6.QtCore import QThread, Signal


class DeleteWorker(QThread):
    # A short status message, e.g. "Deleting venv (12/800)"
    progress = Signal(str)

    # Finished: (deleted_count, failures, was_cancelled)
    # failures is a list of (path, error_text) tuples
    delete_done = Signal(int, object, bool)

    def __init__(self, paths: list[Path]):
        super().__init__()
        self.paths = list(paths)

    def run(self):
        from services.recycle_service import delete

        deleted = 0
        failures = []
        cancelled = False
        total = len(self.paths)

        for index, path in enumerate(self.paths, start=1):
            if self.isInterruptionRequested():
                cancelled = True
                break

            self.progress.emit(f"Deleting {path.name} ({index}/{total})")
            try:
                delete(path)
                deleted += 1
            except Exception as e:
                failures.append((path, str(e)))

        self.delete_done.emit(deleted, failures, cancelled)