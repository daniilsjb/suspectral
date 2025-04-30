from PySide6.QtCore import (
    QPoint,
    QRectF,
    QStandardPaths,
    Signal,
)
from PySide6.QtGui import (
    Qt,
    QAction,
    QContextMenuEvent,
    QMouseEvent,
    QPainter,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QMenu,
    QMessageBox,
    QWidget,
)


class ImageView(QGraphicsView):
    cursor_moved_inside = Signal(QPoint)
    cursor_moved_outside = Signal()
    context_menu_requested = Signal(QMenu)

    ZOOM_MIN = 0.5
    ZOOM_MAX = 100.0

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._zoom: float = 1.0

        self.setScene(QGraphicsScene(self))
        self.image_container = self.scene().addPixmap(QPixmap())

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def set_pixmap(self, pixmap: QPixmap):
        self.image_container.setPixmap(pixmap)

    def reset(self):
        self.scene().clear()
        self.scene().deleteLater()
        self.setScene(QGraphicsScene(self))

        self.image_container = self.scene().addPixmap(QPixmap())
        self.setSceneRect(QRectF())

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
        self.fitInView(self.image_container, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = abs(
            self.transform().m11() or
            self.transform().m12() or
            self.transform().m21() or
            self.transform().m22()
        )

    def save_image(self):
        downloads = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        path, _ = QFileDialog.getSaveFileName(
            caption="Save Image",
            filter="PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;Bitmap (*.bmp)",
            dir=f"{downloads}/Image.png",
        )

        if not path: return
        if not self.image_container.pixmap().save(path):
            QMessageBox.critical(
                self,
                "Export Failed",
                "Couldn't export the image to the specified file path. Please, ensure that you've "
                "selected one of the supported image formats and that the target directory is accessible.",
            )

    def copy_image(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.image_container.pixmap())

    def mouseMoveEvent(self, event: QMouseEvent):
        scene_position = self.mapToScene(event.position().toPoint())
        local_position = self.image_container.mapFromScene(scene_position)

        boundary = self.image_container.pixmap().rect()
        if boundary.contains(local_position.toPoint()):
            self.cursor_moved_inside.emit(QPoint(
                int(local_position.x()),
                int(local_position.y()),
            ))
        else:
            self.cursor_moved_outside.emit()

        super().mouseMoveEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def contextMenuEvent(self, event: QContextMenuEvent):
        if not self.image_container.pixmap().isNull():
            menu = QMenu(self)

            copy_action = QAction("Copy Image", self)
            copy_action.triggered.connect(self.copy_image)
            menu.addAction(copy_action)

            save_action = QAction("Save Image As...", self)
            save_action.triggered.connect(self.save_image)
            menu.addAction(save_action)

            menu.addSeparator()

            self.context_menu_requested.emit(menu)
            menu.exec(event.globalPos())
