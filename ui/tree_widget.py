"""
ui/tree_widget.py

Displays scan candidates as checkable rows with full context.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QColor
from models.candidate import Candidate
from services.file_service import format_size


class CandidateTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(5)
        self.setHeaderLabels([
            "Name",
            "Ecosystem",
            "Score",
            "Size",
            "Label",
        ])

        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
    
    def add_row(self, candidate: Candidate, score: int, label: str, size: int):
        item = QTreeWidgetItem([
            candidate.path.name,
            ", ".join(candidate.ecosystems),
            str(score),
            format_size(size),          # was format_size(get_size(candidate.path))
            label,
        ])

        item.setData(0, Qt.UserRole, candidate.path)
        item.setData(0, Qt.UserRole + 1, size)      # NEW: raw bytes, kept for summing

        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Checked if label == "safe" else Qt.Unchecked)

        item.setTextAlignment(2, Qt.AlignCenter)
        item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        item.setTextAlignment(4, Qt.AlignLeft | Qt.AlignVCenter)

        self.addTopLevelItem(item)

        if label == "safe":
            item.setForeground(4, QColor("#a6e3a1"))
        elif label == "review":
            item.setForeground(4, QColor("#f9e2af"))
        else:
            item.setForeground(4, QColor("#f38ba8"))

    def get_checked(self) -> list[Path]:
        checked = []

        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                checked.append(item.data(0, Qt.UserRole))

        return checked

    def update_savings(self):
        from services.file_service import format_size
        total = 0
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                path = item.data(0, Qt.UserRole)
                try:
                    size = item.data(0, Qt.UserRole + 1) or 0
                    total += size
                except OSError:
                    continue
        return total