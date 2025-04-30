from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


class MetadataView(QStackedWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Base)

        self._placeholder = QLabel("Load a hypercube to see its metadata.")
        self._placeholder.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._placeholder.setContentsMargins(4, 4, 4, 4)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.addWidget(self._placeholder)
        self.addWidget(self._table)

    def set_items(self, metadata: dict[str, object]):
        self._table.setRowCount(len(metadata))
        for row, (key, value) in enumerate(metadata.items()):
            if isinstance(value, list):
                value = [self._stringify(v) for v in value]
                value = "{" + ", ".join(map(str, value)) + "}"

            self._table.setItem(row, 0, QTableWidgetItem(str(key)))
            self._table.setItem(row, 1, QTableWidgetItem(str(value)))

        self.setCurrentWidget(self._table)

    def clear(self):
        self._table.clearContents()
        self._table.setRowCount(0)
        self.setCurrentWidget(self._placeholder)

    @staticmethod
    def _stringify(item: str):
        if item.isdigit():
            return int(item)
        elif item.replace('.', '', 1).isdigit():
            return float(item)
        else:
            return item
