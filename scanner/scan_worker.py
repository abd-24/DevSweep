"""
scanner/scan_worker.py

Runs the scan pipeline on a background thread so the UI never freezes.
The worker never touches any widget. It only sends signals back to the UI.
"""

import traceback
from pathlib import Path

from PySide6.QtCore import QThread, Signal


class ScanWorker(QThread):
    # One candidate finished: (candidate, score, label, size_in_bytes)
    # size uses `object` instead of `int` because Qt's int is 32-bit
    # and would overflow on anything bigger than ~2 GB.
    candidate_ready = Signal(object, int, str, object)

    # A short status message for the UI, e.g. "Analyzing venv (2/8)"
    progress = Signal(str)

    # Everything finished: (total_reclaimable_bytes, candidate_count)
    scan_complete = Signal(object, int)

    # The user cancelled or closed the window mid-scan
    scan_cancelled = Signal()

    # Something crashed: full traceback text
    scan_error = Signal(str)

    def __init__(self, root: Path):
        super().__init__()
        self.root = Path(root)

    def _is_cancelled(self) -> bool:
        return self.isInterruptionRequested()

    def run(self):
        """Runs on the background thread when .start() is called."""
        try:
            from scanner.scanner import scan
            from scanner.detector import detect_candidates, ALL_DELETABLES
            from scanner.classifier import classify
            from services.file_service import get_size

            # Stage 1: walk the folders
            self.progress.emit("Scanning folders...")
            scan_result = scan(
                self.root,
                skip_deletables=ALL_DELETABLES,
                should_cancel=self._is_cancelled,
            )
            if self._is_cancelled():
                self.scan_cancelled.emit()
                return

            # Stage 2: find candidates
            self.progress.emit("Finding candidates...")
            candidates = detect_candidates(scan_result)
            if self._is_cancelled():
                self.scan_cancelled.emit()
                return

            # Stage 3: score and measure each candidate, one at a time
            total_candidates = len(candidates)
            total_reclaimable = 0

            for index, candidate in enumerate(candidates, start=1):
                if self._is_cancelled():
                    self.scan_cancelled.emit()
                    return

                self.progress.emit(
                    f"Analyzing {candidate.path.name} ({index}/{total_candidates})"
                )

                score, label = classify(candidate, self.root)
                size = get_size(candidate.path)  # computed ONCE, reused everywhere

                if label == "safe":
                    total_reclaimable += size

                self.candidate_ready.emit(candidate, score, label, size)

            # Stage 4: done
            self.scan_complete.emit(total_reclaimable, total_candidates)

        except Exception:
            self.scan_error.emit(traceback.format_exc())