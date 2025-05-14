from PySide6.QtCore import (
    QPoint,
    QPointF,
    QRectF,
    Signal,
)
from PySide6.QtGui import (
    Qt,
    QContextMenuEvent,
    QMouseEvent,
    QPainter,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QMenu,
    QWidget,
)


class ImageView(QGraphicsView):
    cursorMovedInside = Signal(QPoint)
    cursorMovedOutside = Signal()
    contextMenuRequested = Signal(QMenu)

    ZOOM_MIN = 0.5
    ZOOM_MAX = 100.0

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._zoom: float = 1.0

        self.setScene(QGraphicsScene(self))
        self._image = self.scene().addPixmap(QPixmap())

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    @property
    def image(self):
        return self._image

    def display(self, pixmap: QPixmap):
        self.image.setPixmap(pixmap)
        self.setSceneRect(self.image.boundingRect())

    def reset(self):
        self.image.setPixmap(QPixmap())
        self.setSceneRect(QRectF(0, 0, 1, 1))

        self.resetTransform()
        self._zoom = 1.0

    def rotate_left(self):
        self.rotate(-90.0)

    def rotate_right(self):
        self.rotate(+90.0)

    def flip_vertically(self):
        self.scale(+1.0, -1.0)

    def flip_horizontally(self):
        self.scale(-1.0, +1.0)

    def zoom(self, factor: float = 1.2):
        zoom = self._zoom * factor
        zoom = max(zoom, self.ZOOM_MIN)
        zoom = min(zoom, self.ZOOM_MAX)

        factor = zoom / self._zoom
        self.scale(factor, factor)
        self._zoom = zoom

    def zoom_in(self, factor: float = 1.2):
        self.zoom(factor)

    def zoom_out(self, factor: float = 1.2):
        self.zoom(1.0 / factor)

    def zoom_fit(self):
        self.fitInView(self.image, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = abs(
            self.transform().m11() or
            self.transform().m12() or
            self.transform().m21() or
            self.transform().m22()
        )

    def mouseMoveEvent(self, event: QMouseEvent):
        scene_position: QPointF = self.mapToScene(event.position().toPoint())
        local_position: QPointF = self.image.mapFromScene(scene_position)

        boundary = self.image.pixmap().rect()
        if boundary.contains(local_position.toPoint()):
            self.cursorMovedInside.emit(QPoint(
                int(local_position.x()),
                int(local_position.y()),
            ))
        else:
            self.cursorMovedOutside.emit()

        super().mouseMoveEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def contextMenuEvent(self, event: QContextMenuEvent):
        if not self.image.pixmap().isNull():
            menu = QMenu(self)
            self.contextMenuRequested.emit(menu)
            menu.exec(event.globalPos())
