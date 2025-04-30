from PySide6.QtCore import QObject, QEvent

from suspectral.image.image_view import ImageView


class Tool(QObject):
    def __init__(self, view: ImageView, parent: QObject | None = None):
        super().__init__(parent)
        self._view = view

    def activate(self):
        """Called whenever the tool is enabled."""
        self._view.viewport().installEventFilter(self)

    def deactivate(self):
        """Called whenever the tool is disabled."""
        self._view.viewport().removeEventFilter(self)
