import numpy as np
from PySide6.QtCore import QObject, Slot, QStandardPaths
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtWidgets import QMenu, QApplication, QFileDialog, QMessageBox

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.image_options_view import ImageOptionsView
from suspectral.view.image.image_view import ImageView


class ImageController(QObject):
    def __init__(self, *,
                 model: HypercubeContainer,
                 image_display_view: ImageView,
                 image_options_view: ImageOptionsView,
                 parent: QObject | None = None):
        super().__init__(parent)

        self._model = model
        self._image_display_view = image_display_view
        self._image_options_view = image_options_view

        self._model.opened.connect(self._handle_hypercube_opened)
        self._model.closed.connect(self._handle_hypercube_closed)

        self._image_options_view.imagedChanged.connect(self._handle_image_changed)
        self._image_display_view.contextMenuRequested.connect(self._handle_context_menu)

    @Slot()
    def _handle_hypercube_opened(self):
        self._image_display_view.reset()
        self._image_options_view.activate()

    @Slot()
    def _handle_hypercube_closed(self):
        self._image_options_view.deactivate()
        self._image_display_view.reset()

    @Slot()
    def _handle_image_changed(self, data: np.ndarray):
        height, width, channels = data.shape
        image_bytes = np.ascontiguousarray((data * 255).astype(np.uint8)).tobytes()
        image = QImage(image_bytes, width, height, channels * width, QImage.Format.Format_RGB888)
        self._image_display_view.display(QPixmap.fromImage(image))

    @Slot()
    def _handle_context_menu(self, menu: QMenu):
        copy_action = QAction("Copy Image", self)
        copy_action.triggered.connect(self.copy_image)
        menu.addAction(copy_action)

        save_action = QAction("Save Image As...", self)
        save_action.triggered.connect(self.save_image)
        menu.addAction(save_action)

        menu.addSeparator()

    @Slot()
    def copy_image(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self._image_display_view.image.pixmap())

    @Slot()
    def save_image(self):
        downloads = QStandardPaths \
            .writableLocation(QStandardPaths.StandardLocation.DownloadLocation)

        name = self._model.hypercube.name
        path, _ = QFileDialog.getSaveFileName(
            caption="Save Image",
            filter="PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;Bitmap (*.bmp)",
            dir=f"{downloads}/{name}.png",
        )

        if not path: return
        if not self._image_display_view.image.pixmap().save(path):
            QMessageBox.critical(
                self._image_display_view,
                "Export Failed",
                "Couldn't export the image to the specified file path. Please, ensure that you've "
                "selected one of the supported image formats and that the target directory is accessible.",
            )
