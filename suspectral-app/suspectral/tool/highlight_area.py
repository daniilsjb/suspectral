from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsRectItem, QWidget


class AreaHighlight(QGraphicsRectItem):
    """
    A graphics item used to highlight a rectangular area on a scene.

    This highlight is rendered as a semi-transparent filled rectangle with a faint border,
    used for marking selected regions or areas of interest.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        r, g, b = 78, 155, 207

        pen = QPen(QColor(r, g, b, 100))
        pen.setCosmetic(True)
        pen.setWidth(1)
        self.setPen(pen)

        brush = QBrush(QColor(r, g, b, 75))
        self.setBrush(brush)
