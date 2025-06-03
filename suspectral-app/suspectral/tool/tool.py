from PySide6.QtCore import QObject

from suspectral.view.image.image_view import ImageView


class Tool(QObject):
    """
    Base class for tools that interact with the image view.

    Parameters
    ----------
    view : ImageView
        The image view instance this tool is attached to.
    parent : QObject or None, optional
        The parent object of the tool, by default None.
    """

    def __init__(self, view: ImageView, parent: QObject | None = None):
        super().__init__(parent)
        self._view = view

    def activate(self):
        """Called whenever the tool is enabled."""
        self._view.viewport().installEventFilter(self)

    def deactivate(self):
        """Called whenever the tool is disabled."""
        self._view.viewport().removeEventFilter(self)
