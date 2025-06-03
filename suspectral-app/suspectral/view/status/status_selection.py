from PySide6.QtCore import QRect
from PySide6.QtWidgets import QWidget

from suspectral.view.status.status_view_item import StatusViewItem
from suspectral.theme_pixmap import ThemePixmap


class SelectionStatus(StatusViewItem):
    """
    A widget that displays the dimensions of a selected rectangular region.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget, if any.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("select.svg"), parent)

    def set(self, rectangle: QRect):
        """
        Update the displayed size based on the selected rectangle.

        Parameters
        ----------
        rectangle : QRect
            The selection rectangle (inclusive bounds).
        """
        self._label.setText(f"{rectangle.width() - 1} × {rectangle.height() - 1}px")
