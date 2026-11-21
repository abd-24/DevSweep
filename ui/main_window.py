"""
ui/main_window.py

The main application window. Acts as container for all UI components.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit
)
from ui.tree_widget import CandidateTree
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui.styles import APP_STYLESHEET
from datetime import datetime
from time import perf_counter
from scanner.scan_worker import ScanWorker
from services.file_service import format_size
from services.report_service import generate_scan_report, save_report

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setWindowTitle("DevSweep")
        self.setMinimumSize(900, 600)

        # central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)
        
        self.worker = None      # must be self.worker, or it gets garbage-collected
        self._candidates = []
        self._scores = {}       # path -> (score, label), same shape as before
        self._sizes = {}        # path -> bytes, computed once by the worker
        self._root = None

        self._build_folder_row()    # top section
        self._build_results_area()  # middle section
        self._build_action_row()    # bottom section
        self.tree.itemChanged.connect(self._on_selection_changed)
        self._apply_styles()

    def _build_folder_row(self):
        row = QHBoxLayout()
        self.path_display = QLineEdit()
        self.path_display.setPlaceholderText("Select a folder to scan...")
        self.path_display.setReadOnly(True)
        self.browse_button = QPushButton("Browse")
        row.addWidget(QLabel("Path:"))
        row.addWidget(self.path_display)
        row.addWidget(self.browse_button)
        self.layout.addLayout(row)
        self.browse_button.clicked.connect(self._on_browse)
        self.browse_button.setObjectName("browse_button")
        
    def _build_results_area(self):
        self.tree = CandidateTree()
        self.savings_label = QLabel("Potential savings: 0 B")
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.savings_label)
        self.savings_label.setObjectName("savings_label")

    def _on_selection_changed(self):
        from services.file_service import format_size
        total = self.tree.update_savings()
        self.savings_label.setText(f"Potential savings: {format_size(total)}")
    
    def _build_action_row(self):
        row = QHBoxLayout()
        self.auto_select_btn = QPushButton("Auto Select")
        self.select_all_btn = QPushButton("Select All")
        self.delete_btn = QPushButton("Delete Selected")
        self.dry_run_btn = QPushButton("Dry Run")
        row.addWidget(self.auto_select_btn)
        row.addWidget(self.select_all_btn)
        row.addWidget(self.delete_btn)
        row.addWidget(self.dry_run_btn)
        self.layout.addLayout(row)
        self.select_all_btn.clicked.connect(self._on_select_all)
        self.auto_select_btn.clicked.connect(self._on_auto_select)
        self.delete_btn.clicked.connect(self._on_delete)
        self.dry_run_btn.clicked.connect(self._on_dry_run)
        self.delete_btn.setObjectName("delete_button")
    def _on_browse(self):
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.path_display.setText(folder)
            self._run_scan(folder)

    def _run_scan(self, folder: str):
        # Never run two scans at once
        if self.worker is not None and self.worker.isRunning():
            return

        self._root = Path(folder)
        self._candidates = []
        self._scores = {}
        self._sizes = {}

        self.tree.clear()
        self.tree.setSortingEnabled(False)   # sorting while rows stream in makes them jump
        self._set_scanning(True)

        self.worker = ScanWorker(self._root)
        self.worker.candidate_ready.connect(self._on_candidate_ready)
        self.worker.progress.connect(self._on_progress)
        self.worker.scan_complete.connect(self._on_scan_complete)
        self.worker.scan_cancelled.connect(self._on_scan_cancelled)
        self.worker.scan_error.connect(self._on_scan_error)
        self._scan_started = perf_counter()   # "press the stopwatch"
        self.worker.start()                  # start(), NOT run()

    def _set_scanning(self, scanning: bool):
        """Lock the buttons that must not be used mid-scan."""
        for btn in (self.browse_button, self.delete_btn, self.dry_run_btn,
                    self.auto_select_btn, self.select_all_btn):
            btn.setEnabled(not scanning)

    def _on_candidate_ready(self, candidate, score, label, size):
        self._candidates.append(candidate)
        self._scores[candidate.path] = (score, label)
        self._sizes[candidate.path] = size
        self.tree.add_row(candidate, score, label, size)

    def _on_progress(self, text: str):
        self.statusBar().showMessage(text)

    def _on_scan_complete(self, total_reclaimable, count):
        self.tree.setSortingEnabled(True)
        self._set_scanning(False)
        self.savings_label.setText(f"Potential savings: {format_size(total_reclaimable)}")

        elapsed = perf_counter() - self._scan_started
        self.statusBar().showMessage(f"Scan complete: {count} candidates in {elapsed:.1f}s")

        try:
            report = generate_scan_report(self._candidates, self._scores, self._sizes, self._root)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_report(report, Path("reports") / f"scan_{timestamp}.json")
        except OSError as e:
            from ui.dialogs import show_error
            show_error(self, f"Could not save scan report: {e}")
    def _on_scan_cancelled(self):
        self.tree.setSortingEnabled(True)
        self._set_scanning(False)
        self.statusBar().showMessage("Scan cancelled")

    def _on_scan_error(self, tb_text: str):
        from ui.dialogs import show_error
        print(tb_text)                       # full traceback in the console for you
        self.tree.setSortingEnabled(True)
        self._set_scanning(False)
        self.statusBar().showMessage("Scan failed")
        show_error(self, f"Scan failed: {tb_text.strip().splitlines()[-1]}")

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait()               # block until the thread really stops
        event.accept()

    def _on_select_all(self):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setCheckState(0, Qt.Checked)

    def _on_auto_select(self):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            label = item.text(4)
            if label == "safe":
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
    
    def _on_dry_run(self):
        from ui.dialogs import show_dry_run
        checked_paths = self.tree.get_checked()
        if not checked_paths:
            from ui.dialogs import show_error
            show_error(self, "No items selected for dry run.")
            return
        
        from services.file_service import get_size, format_size
        sizes = {path: format_size(self._sizes.get(path, 0)) for path in checked_paths}
        show_dry_run(self, checked_paths, sizes)
    
    def _on_delete(self):
        from ui.dialogs import confirm_delete, show_error
        checked_paths = self.tree.get_checked()
        if not checked_paths:
            show_error(self, "No items selected for deletion.")
            return

        total = format_size(sum(self._sizes.get(p, 0) for p in checked_paths))
        confirmed = confirm_delete(self, checked_paths, total)
        if confirmed:
            from services.recycle_service import delete
            for path in checked_paths:
                try:
                    delete(path)
                except Exception as e:
                    show_error(self, f"Failed to delete {path}: {e}")
            self._run_scan(self.path_display.text())   # rescan only after a real delete

    #Styling
    def _apply_styles(self):
       self.setStyleSheet(APP_STYLESHEET)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())