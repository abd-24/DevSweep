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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevSweep")
        self.setMinimumSize(900, 600)

        # central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)

        self._build_folder_row()    # top section
        self._build_results_area()  # middle section
        self._build_action_row()    # bottom section
        self.tree.itemChanged.connect(self._on_selection_changed)

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
        
    def _build_results_area(self):
        self.tree = CandidateTree()
        self.savings_label = QLabel("Potential savings: 0 B")
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.savings_label)

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

    def _on_browse(self):
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.path_display.setText(folder)
            self._run_scan(folder)

    def _run_scan(self, folder: str):
        from pathlib import Path
        from scanner.scanner import scan
        from scanner.detector import detect_candidates, ALL_DELETABLES
        from scanner.classifier import classify
        from services.file_service import format_size

        root = Path(folder)
        scan_result = scan(root, skip_deletables=ALL_DELETABLES)
        candidates = detect_candidates(scan_result)

        scores = {}
        total_reclaimable = 0
        for c in candidates:
            score, label = classify(c, root)
            scores[c.path] = (score, label)
            if label == "safe":
                from services.file_service import get_size
                total_reclaimable += get_size(c.path)

        self.tree.populate(candidates, scores)
        self.savings_label.setText(f"Potential savings: {format_size(total_reclaimable)}")

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
        sizes = {path: format_size(get_size(path)) for path in checked_paths}
        show_dry_run(self, checked_paths, sizes)
    
    def _on_delete(self):
        from ui.dialogs import confirm_delete, show_error
        checked_paths = self.tree.get_checked()
        if not checked_paths:
            show_error(self, "No items selected for deletion.")
            return
        from services.file_service import get_size, format_size
        total = format_size(sum(get_size(p) for p in checked_paths))
        confirmed = confirm_delete(self, checked_paths, total)
        if confirmed:
                from services.recycle_service import delete
                for path in checked_paths:
                    try:
                        delete(path)
                    except Exception as e:
                        show_error(self, f"Failed to delete {path}: {e}")
        self._run_scan(self.path_display.text())
        self.tree.update_savings()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())