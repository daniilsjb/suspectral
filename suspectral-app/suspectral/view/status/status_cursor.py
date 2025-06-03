from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QWidget

from suspectral.view.status.status_view_item import StatusViewItem
from suspectral.theme_pixmap import ThemePixmap


class CursorStatus(StatusViewItem):
    """A status widget that displays the current cursor position in pixel coordinates.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("cursor.svg"), parent)

    def set(self, position: QPoint):
        """
        Update the label text to reflect the given cursor position.

        Parameters
        ----------
        position : QPoint
            The cursor's current position in pixel coordinates.
        """
        self._label.setText(f"{position.x()}, {position.y()}px")
