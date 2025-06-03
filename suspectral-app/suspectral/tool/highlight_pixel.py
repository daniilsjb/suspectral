from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QWidget


class PixelHighlight(QGraphicsRectItem):
    """
    A graphics item used to highlight a single pixel on a scene.

    The highlight is drawn as a white semi-transparent rectangle with a fixed-width outline,
    used for marking a selected or hovered pixel.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        pen = QPen(QColor(255, 255, 255, 200))
        pen.setWidth(3)
        pen.setCosmetic(True)
        self.setPen(pen)
