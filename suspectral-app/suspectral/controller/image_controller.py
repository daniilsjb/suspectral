import itertools
import numpy as np
from PySide6.QtCore import QObject, Slot, QStandardPaths, QPoint
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtWidgets import QMenu, QApplication, QFileDialog, QMessageBox

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.theme_icon import ThemeIcon
from suspectral.tool.manager import ToolManager
from suspectral.view.image.image_controls_view import ImageControlsView
from suspectral.view.image.image_view import ImageView


class ImageController(QObject):
    """
    Controller synchronizing image rendering and user interaction in the image views.

    Parameters
    ----------
    model : HypercubeContainer
        The data model that holds the currently loaded hyperspectral cube.
    tools : ToolManager
        The manager for user-interaction tools such as inspect and selection tools.
    image_display_view : ImageView
        The widget responsible for rendering the synthesized image.
    image_controls_view : ImageControlsView
        The widget that provides coloring and visualization configuration controls.
    parent : QObject or None, optional
        The parent object of the controller, by default None.
    """

    def __init__(self, *,
                 tools: ToolManager,
                 model: HypercubeContainer,
                 image_display_view: ImageView,
                 image_controls_view: ImageControlsView,
                 parent: QObject | None = None):
        super().__init__(parent)

        self._model = model
        self._image_display_view = image_display_view
        self._image_controls_view = image_controls_view

        model.opened.connect(self._handle_hypercube_opened)
        model.closed.connect(self._handle_hypercube_closed)

        image_controls_view.imagedChanged.connect(self._handle_image_changed)
        image_display_view.contextMenuRequested.connect(self._handle_context_menu)

        tools.toolChanged.connect(self._handle_tool_changed)

        tools.inspect.pixelClicked.connect(self._handle_pixel_clicked)
        tools.inspect.pixelCleared.connect(self._handle_pixel_cleared)

        tools.area.selectionMoved.connect(self._handle_selection_changed)
        tools.area.selectionEnded.connect(self._handle_selection_changed)
        tools.area.selectionSampled.connect(self._handle_selection_sampled)

    @Slot()
    def _handle_tool_changed(self):
        self._image_controls_view.clear_reference_points()

    @Slot()
    def _handle_selection_changed(self):
        self._image_controls_view.clear_reference_points()

    @Slot()
    def _handle_selection_sampled(self, xs: np.ndarray, ys: np.ndarray):
        for point in [QPoint(x, y) for y, x in itertools.product(ys, xs)]:
            self._image_controls_view.add_reference_points(point)

    @Slot()
    def _handle_pixel_clicked(self, point: QPoint):
        self._image_controls_view.add_reference_points(point)

    @Slot()
    def _handle_pixel_cleared(self):
        self._image_controls_view.clear_reference_points()

    @Slot()
    def _handle_hypercube_opened(self):
        self._image_display_view.reset()
        self._image_controls_view.activate()

    @Slot()
    def _handle_hypercube_closed(self):
        self._image_controls_view.deactivate()
        self._image_display_view.reset()

    @Slot()
    def _handle_image_changed(self, data: np.ndarray):
        import hashlib
        print(hashlib.md5(np.ascontiguousarray(data).tobytes()).hexdigest())

        height, width, channels = data.shape
        image_bytes = np.ascontiguousarray((data * 255).astype(np.uint8)).tobytes()
        image = QImage(image_bytes, width, height, channels * width, QImage.Format.Format_RGB888)
        self._image_display_view.display(QPixmap.fromImage(image))

    @Slot()
    def _handle_context_menu(self, menu: QMenu):
        copy_action = QAction("Copy Image", self)
        copy_action.setIcon(ThemeIcon("copy.svg"))
        copy_action.triggered.connect(self.copy_image)
        menu.addAction(copy_action)

        save_action = QAction("Save Image As...", self)
        save_action.setIcon(ThemeIcon("image.svg"))
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

        path, _ = QFileDialog.getSaveFileName(
            caption="Save Image",
            filter="PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;Bitmap (*.bmp)",
            dir=f"{downloads}/{self._model.hypercube.name}.png",
        )

        if not path: return
        if not self._image_display_view.image.pixmap().save(path):
            QMessageBox.critical(
                self._image_display_view,
                "Export Failed",
                "Couldn't export the image to the specified file path. Please, ensure that you've "
                "selected one of the supported image formats and that the target directory is accessible.",
            )
