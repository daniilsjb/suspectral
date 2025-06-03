from PySide6.QtCore import QPoint, QRect, Slot
from PySide6.QtWidgets import QWidget, QStatusBar

from suspectral.model.hypercube import Hypercube
from suspectral.view.status.status_cursor import CursorStatus
from suspectral.view.status.status_memory import MemoryStatus
from suspectral.view.status.status_selection import SelectionStatus
from suspectral.view.status.status_shape import ShapeStatus
from suspectral.view.status.status_wavelength import WavelengthStatus


class StatusView(QStatusBar):
    """
    A status bar widget that displays contextual information about the currently
    loaded hyperspectral data, including shape, memory usage, cursor position,
    selection area, and wavelength range.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget of the status bar.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setContentsMargins(2, 2, 2, 2)

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

    @Slot()
    def update_hypercube(self, hypercube: Hypercube):
        """
        Update the static metadata from the given hypercube.

        Parameters
        ----------
        hypercube : Hypercube
            The hypercube containing metadata to be displayed.
        """
        self._shape_status.set(
            hypercube.num_cols,
            hypercube.num_rows,
            hypercube.num_bands,
        )
        self._memory_status.set(
            hypercube.num_bytes,
        )

        if hypercube.wavelengths is None:
            self._wavelength_status.clear()
            return

        self._wavelength_status.set(
            hypercube.wavelengths,
            hypercube.wavelengths_unit,
        )

    @Slot()
    def update_cursor(self, position: QPoint):
        """
        Update the displayed cursor position.

        Parameters
        ----------
        position : QPoint
            The current cursor position in image coordinates.
        """
        self._cursor_status.set(position)

    @Slot()
    def clear_cursor(self):
        """Clear the displayed cursor position."""
        self._cursor_status.clear()

    @Slot()
    def update_selection(self, rectangle: QRect):
        """
        Update the displayed selection area.

        Parameters
        ----------
        rectangle : QRect
            The rectangular selection area.
        """
        self._selection_status.set(rectangle)

    @Slot()
    def clear_selection(self):
        """Clear the displayed selection area."""
        self._selection_status.clear()

    @Slot()
    def clear(self):
        """Clear all status indicators, resetting the status view."""
        self._shape_status.clear()
        self._memory_status.clear()
        self._cursor_status.clear()
        self._selection_status.clear()
        self._wavelength_status.clear()
