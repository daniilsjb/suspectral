from PySide6.QtCore import Qt, QPoint, Slot
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from suspectral.colors import get_color


class SelectionView(QStackedWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Base)

        self._placeholder = QLabel("Select pixels to view their properties.")
        self._placeholder.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._placeholder.setContentsMargins(4, 4, 4, 4)

        self._table = QTableWidget(self)
        self._table.setColumnCount(3)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setHorizontalHeaderLabels(["Legend", "X", "Y"])

        self.addWidget(self._placeholder)
        self.addWidget(self._table)

    @Slot()
    def add_point(self, point: QPoint):
        self.setCurrentWidget(self._table)
        self._append(point)

    @Slot()
    def add_points(self, points: list[QPoint]):
        self.setCurrentWidget(self._table)
        for point in points:
            self._append(point)

    @Slot()
    def clear(self):
        self._table.clearContents()
        self._table.setRowCount(0)
        self.setCurrentWidget(self._placeholder)

    def _append(self, point: QPoint):
        row = self._table.rowCount()
        self._table.insertRow(row)

        item_color = QTableWidgetItem()
        item_color.setBackground(get_color(row))
        item_color.setFlags(item_color.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        item_color.setFlags(item_color.flags() & ~Qt.ItemFlag.ItemIsEditable)

        item_pos_x = QTableWidgetItem(str(point.x()))
        item_pos_x.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        item_pos_y = QTableWidgetItem(str(point.y()))
        item_pos_y.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self._table.setItem(row, 0, item_color)
        self._table.setItem(row, 1, item_pos_x)
        self._table.setItem(row, 2, item_pos_y)
