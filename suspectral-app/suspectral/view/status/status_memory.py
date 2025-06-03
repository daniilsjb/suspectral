from PySide6.QtWidgets import QWidget

from suspectral.view.status.status_view_item import StatusViewItem
from suspectral.theme_pixmap import ThemePixmap


class MemoryStatus(StatusViewItem):
    """
    A status widget that displays memory usage in a human-readable format.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("database.svg"), parent)

    def set(self, num_bytes: int):
        """
        Update the label text to reflect the given memory size.

        Parameters
        ----------
        num_bytes : int
            The number of bytes to display; must be non-negative.
        """
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
