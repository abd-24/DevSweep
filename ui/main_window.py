"""
ui/main_window.py

The main application window. Acts as container for all UI components.
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit
)


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
        
    def _build_results_area(self):
        self.results_label = QLabel("No scan results yet.")
        self.savings_label = QLabel("Potential savings: 0 B")
        self.layout.addWidget(self.results_label)
        self.layout.addWidget(self.savings_label)

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
    


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())