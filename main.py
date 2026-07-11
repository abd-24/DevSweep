"""
main.py

Entry point for DevSweep.
"""

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PySide6.QtGui import QIcon

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("assets/icon.png"))
if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(app.exec())