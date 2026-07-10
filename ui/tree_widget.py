"""
ui/tree_widget.py

Displays scan candidates as checkable rows with full context.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QColor
from models.candidate import Candidate
from services.file_service import get_size, format_size


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
        self.itemChanged.connect(self._on_item_changed)

    def populate(self, candidates: list[Candidate], scores: dict[Path, tuple[int, str]]):
        self.clear()

        for candidate in candidates:
            score, label = scores.get(candidate.path, (0, "ignore"))

            item = QTreeWidgetItem([
                candidate.path.name,
                candidate.ecosystem,
                str(score),
                format_size(get_size(candidate.path)),
                label,
            ])

            item.setData(0, Qt.UserRole, candidate.path)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            # Auto-check high-confidence items
            item.setCheckState(
                0,
                Qt.Checked if label == "safe" else Qt.Unchecked,
            )

            item.setTextAlignment(2, Qt.AlignCenter)
            item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
            item.setTextAlignment(4, Qt.AlignLeft | Qt.AlignVCenter)

            self.addTopLevelItem(item)

            # color code the label column
            if label == "safe":
                item.setForeground(4, QColor("#a6e3a1"))   # green
            elif label == "review":
                item.setForeground(4, QColor("#f9e2af"))   # yellow
            else:
                item.setForeground(4, QColor("#f38ba8"))   # red

    def get_checked(self) -> list[Path]:
        checked = []

        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                checked.append(item.data(0, Qt.UserRole))

        return checked
    
    def _on_item_changed(self, item, column):
        if column == 0:  # checkbox column
            self.update_savings()

    def update_savings(self):
        from services.file_service import get_size, format_size
        total = 0
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                path = item.data(0, Qt.UserRole)
                try:
                    total += get_size(path)
                except OSError:
                    continue
        return total