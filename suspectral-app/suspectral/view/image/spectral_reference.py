import numpy as np
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QPixmap, QIcon
from PySide6.QtWidgets import QComboBox, QWidget, QVBoxLayout

from suspectral.colors import get_color
from suspectral.model.hypercube_container import HypercubeContainer


class SpectralReference(QWidget):
    """
    A widget for managing and selecting reference spectra in a hyperspectral image.

    Parameters
    ----------
    model : HypercubeContainer
        The container holding the hyperspectral data.
    parent : QWidget or None, optional
        The parent QWidget of this widget, by default None.
    """

    def __init__(self, model: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._model = model
        self._points: list[QPoint] = []
        self._select = QComboBox(self)
        self._select.addItem("Select...")

        layout = QVBoxLayout(self)
        layout.addWidget(self._select)
        layout.setContentsMargins(0, 0, 0, 0)

    def clear(self):
        """Clears all reference points and resets the selection dropdown."""
        self._points.clear()
        self._select.clear()
        self._select.addItem("Select...")

    def add(self, point: QPoint):
        """
        Adds a reference point and updates the dropdown menu.

        Parameters
        ----------
        point : QPoint
            The (x, y) coordinates of the point to be added.
        """
        self._points.append(point)
        index = len(self._points) - 1
        color = self._mk_color_icon(get_color(index))
        self._select.addItem(color, f"Selection ({index + 1})")

    def get(self) -> np.ndarray | None:
        """
        Retrieves the spectral data from the currently selected reference point.

        Returns
        -------
        np.ndarray or None
            The spectral data at the selected point as a 1D NumPy array, or None
            if no selection is made.
        """
        if self._select.currentIndex() == 0:
            return None

        index = self._select.currentIndex() - 1
        point = self._points[index]

        return self._model.hypercube.read_pixel(point.y(), point.x())

    @staticmethod
    def _mk_color_icon(color: QColor, size: int = 12):
        pixmap = QPixmap(size, size)
        pixmap.fill(color)
        return QIcon(pixmap)
