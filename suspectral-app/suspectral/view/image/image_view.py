from PySide6.QtCore import QPoint, QPointF, QRectF, Signal
from PySide6.QtGui import (
    Qt,
    QContextMenuEvent,
    QMouseEvent,
    QPainter,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QMenu,
    QWidget,
)


class ImageView(QGraphicsView):
    """
    A widget for displaying and interacting with images using QGraphicsView.

    Signals
    -------
    cursorMovedInside(QPoint)
        Emitted when the mouse cursor moves inside the boundaries of the displayed image.
        Provides the cursor position in image coordinates.

    cursorMovedOutside()
        Emitted when the mouse cursor moves outside the image boundaries.

    contextMenuRequested(QMenu)
        Emitted when the context menu is requested (usually by right-clicking) on the image.
        Provides the QMenu object for adding custom actions.

    Attributes
    ----------
    ZOOM_MIN : float
        Minimum allowed zoom factor.

    ZOOM_MAX : float
        Maximum allowed zoom factor.
    """

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

    def display(self, pixmap: QPixmap):
        """
        Display the given QPixmap in the view and update the scene rectangle.

        Parameters
        ----------
        pixmap : QPixmap
            The image to display.
        """
        self.image.setPixmap(pixmap)
        self.setSceneRect(self.image.boundingRect())

    def reset(self):
        """Clear the currently displayed image and reset zoom and transformations."""
        self.image.setPixmap(QPixmap())
        self.setSceneRect(QRectF(0, 0, 1, 1))

        self.resetTransform()
        self._zoom = 1.0

    def rotate_left(self):
        """Rotate the image 90 degrees counterclockwise."""
        self.rotate(-90.0)

    def rotate_right(self):
        """Rotate the image 90 degrees clockwise."""
        self.rotate(+90.0)

    def flip_vertically(self):
        """Flip the image on the y-axis."""
        self.scale(+1.0, -1.0)

    def flip_horizontally(self):
        """Flip the image on the x-axis."""
        self.scale(-1.0, +1.0)

    def zoom(self, factor: float = 1.2):
        """Zoom the view by the given factor, clamped to allowed zoom limits."""
        zoom = self._zoom * factor
        zoom = max(zoom, self.ZOOM_MIN)
        zoom = min(zoom, self.ZOOM_MAX)

        factor = zoom / self._zoom
        self.scale(factor, factor)
        self._zoom = zoom

    def zoom_in(self, factor: float = 1.2):
        """Zoom in the view by the given factor."""
        self.zoom(factor)

    def zoom_out(self, factor: float = 1.2):
        """Zoom out the view by the given factor."""
        self.zoom(1.0 / factor)

    def zoom_fit(self):
        """Adjust the zoom level to fit the entire image in the view."""
        self.fitInView(self.image, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = abs(
            self.transform().m11() or
            self.transform().m12() or
            self.transform().m21() or
            self.transform().m22()
        )

    @property
    def image(self) -> QGraphicsPixmapItem:
        """The scene graphics item displaying the image."""
        return self._image

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
