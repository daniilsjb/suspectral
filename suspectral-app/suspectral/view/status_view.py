import numpy as np
from PySide6.QtCore import Qt, QPoint, QRect, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QStatusBar, QLabel, QHBoxLayout

from suspectral.model.hypercube import Hypercube
from suspectral.widget.theme_pixmap import ThemePixmap


class StatusView(QStatusBar):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._cursor_status = CursorStatus(self)
        self._cursor_status.setFixedWidth(100)
        self.addWidget(self._cursor_status)

        self._selection_status = SelectionStatus(self)
        self._selection_status.setFixedWidth(120)
        self.addWidget(self._selection_status)

        self._shape_status = ShapeStatus(self)
        self._shape_status.setFixedWidth(150)
        self.addPermanentWidget(self._shape_status)

        self._wavelength_status = WavelengthStatus(self)
        self._wavelength_status.setFixedWidth(180)
        self.addPermanentWidget(self._wavelength_status)

        self._memory_status = MemoryStatus(self)
        self._memory_status.setFixedWidth(120)
        self.addPermanentWidget(self._memory_status)

        self.setContentsMargins(2, 2, 2, 2)

    @Slot()
    def update_hypercube(self, hypercube: Hypercube):
        self._shape_status.set(
            num_cols=hypercube.num_cols,
            num_rows=hypercube.num_rows,
            num_bands=hypercube.num_bands,
        )

        self._memory_status.set(
            num_bytes=hypercube.num_bytes,
        )

        if hypercube.wavelengths is not None:
            self._wavelength_status.set(
                hypercube.wavelengths,
                hypercube.wavelengths_unit,
            )
        else:
            self._wavelength_status.clear()

    @Slot()
    def update_cursor(self, position: QPoint):
        self._cursor_status.set(position)

    def clear_cursor(self):
        self._cursor_status.clear()

    @Slot()
    def update_selection(self, rectangle: QRect):
        self._selection_status.set(rectangle)

    def clear_selection(self):
        self._selection_status.clear()

    @Slot()
    def clear(self):
        self._shape_status.clear()
        self._memory_status.clear()
        self._cursor_status.clear()
        self._wavelength_status.clear()


class StatusBarItem(QWidget):
    def __init__(self, pixmap: QPixmap, parent: QWidget | None = None):
        super().__init__(parent)

        pixmap = pixmap.scaled(16, 16, mode=Qt.TransformationMode.SmoothTransformation)

        self._icon = QLabel()
        self._icon.setPixmap(pixmap)
        self._label = QLabel()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

        layout.addWidget(self._icon)
        layout.addWidget(self._label)

    def clear(self):
        self._label.clear()


class CursorStatus(StatusBarItem):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("cursor.svg"), parent)

    def set(self, position: QPoint):
        self._label.setText(f"{position.x()}, {position.y()}px")


class SelectionStatus(StatusBarItem):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("select.svg"), parent)

    def set(self, rectangle: QRect):
        self._label.setText(f"{rectangle.width() - 1} × {rectangle.height() - 1}px")


class ShapeStatus(StatusBarItem):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("shape.svg"), parent)

    def set(self, num_cols: int, num_rows: int, num_bands: int):
        self._label.setText(f"{num_cols} × {num_rows} × {num_bands}")


class WavelengthStatus(StatusBarItem):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("wave.svg"), parent)

    def set(self, wavelengths: np.ndarray, wavelengths_unit: str | None = None):
        unit = f" ({wavelengths_unit})" if wavelengths_unit else ""
        diff = np.round(np.diff(wavelengths), 2)
        step = f" : {diff[0]:g}" if np.all(diff == diff[0]) else ""

        wave_min = np.round(wavelengths.min(), 2)
        wave_max = np.round(wavelengths.max(), 2)

        self._label.setText(f"{wave_min:g} : {wave_max:g}{step}{unit}")


class MemoryStatus(StatusBarItem):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("database.svg"), parent)

    def set(self, num_bytes: int):
        self._label.setText(self._stringify(num_bytes))

    @staticmethod
    def _stringify(num_bytes: int) -> str:
        assert num_bytes >= 0
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = float(num_bytes)
        for unit in units:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} EB"
