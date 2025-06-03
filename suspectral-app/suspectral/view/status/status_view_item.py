from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class StatusViewItem(QWidget):
    """
    A small widget combining an icon and a text label, suitable for a status bar.

    Parameters
    ----------
    pixmap : QPixmap
        The icon to display next to the label.

    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    def __init__(self, pixmap: QPixmap, parent: QWidget | None = None):
        super().__init__(parent)

        pixmap = pixmap \
            .scaled(16, 16, mode=Qt.TransformationMode.SmoothTransformation)

        self._icon = QLabel()
        self._icon.setPixmap(pixmap)
        self._label = QLabel()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._icon)
        layout.addWidget(self._label)

    def clear(self):
        """Clear the label text content, leaving only the icon visible."""
        self._label.clear()
