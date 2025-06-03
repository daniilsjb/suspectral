from PySide6.QtCore import QPoint, QRectF
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsEllipseItem, QWidget


class PointHighlight(QGraphicsItemGroup):
    """
    A visual indicator for highlighting a specific point on an image view.

    This graphics item group draws a small rectangle (mapped to scene coordinates)
    and a circle centered at the specified point to form a crosshair-style highlight.

    Parameters
    ----------
    view : ImageView
        The image view used to map image-space coordinates to scene-space.
    point : QPoint
        The point to be highlighted.
    color : QColor
        The color of the highlight stroke.
    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    def __init__(self, view, point: QPoint, color: QColor, parent: QWidget | None = None):
        super().__init__(parent)

        pen = QPen(color)
        pen.setWidth(3)
        pen.setCosmetic(True)

        rect = QRectF(point.x(), point.y(), 1, 1)
        scene_rect = view.image.mapRectToScene(rect)

        circle_radius = 10
        circle_rect = QRectF(
            point.x() - circle_radius / 2 + 0.5,
            point.y() - circle_radius / 2 + 0.5,
            circle_radius,
            circle_radius,
        )

        crosshair_r = QGraphicsRectItem(scene_rect)
        crosshair_c = QGraphicsEllipseItem(circle_rect)

        crosshair_r.setPen(pen)
        crosshair_c.setPen(pen)

        self.addToGroup(crosshair_r)
        self.addToGroup(crosshair_c)
