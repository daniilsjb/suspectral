from typing import cast

from PySide6.QtCore import QEvent, Qt, Signal, QPoint, QObject, Slot
from PySide6.QtGui import QMouseEvent, QAction
from PySide6.QtWidgets import QMenu

from suspectral.colors import get_color
from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.highlight_pixel import PixelHighlight
from suspectral.tool.highlight_point import PointHighlight
from suspectral.tool.tool import Tool
from suspectral.view.image.image_view import ImageView


class InspectTool(Tool):
    """
    Tool for inspecting individual pixels in an image view.

    This tool allows users to click on pixels to select them, optionally selecting
    multiple pixels with the Control key. It provides visual feedback such as a
    crosshair overlay and pixel highlight. Selected spectra can be exported using
    a context menu with registered exporters.

    Signals
    -------
    pixelClicked : QPoint
        Emitted when a new pixel is selected by the user.
    pixelCleared : None
        Emitted when the current selection is cleared.

    Parameters
    ----------
    view : ImageView
        The image view widget where interaction occurs.
    container : HypercubeContainer
        The hypercube model containing spectral data.
    exporters : list[Exporter]
        Exporters instances available for exporting selected pixel spectra.
    """

    pixelClicked = Signal(QPoint)
    pixelCleared = Signal()

    def __init__(self, view: ImageView, container: HypercubeContainer, exporters: list[Exporter]):
        super().__init__(view)
        self._container = container
        self._exporters = exporters

        self._points: list[QPoint] = []
        self._crosshair: list[PointHighlight] = []
        self._highlight = None

    def activate(self):
        super().activate()
        self._view.contextMenuRequested.connect(self._handle_context_menu)

    def deactivate(self):
        self._view.contextMenuRequested.disconnect(self._handle_context_menu)
        self._remove_highlight()
        self._remove_crosshair()
        self._view.unsetCursor()
        super().deactivate()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Enter:
            return self._handle_enter(event)
        if event.type() == QEvent.Type.Leave:
            return self._handle_leave(event)
        if event.type() == QEvent.Type.MouseMove:
            return self._handle_mouse_move(cast(QMouseEvent, event))
        if event.type() == QEvent.Type.MouseButtonRelease:
            return self._handle_mouse_release(cast(QMouseEvent, event))

        return super().eventFilter(watched, event)

    def _handle_enter(self, _: QEvent) -> bool:
        self._view.setCursor(Qt.CursorShape.PointingHandCursor)
        return False

    def _handle_leave(self, _: QEvent) -> bool:
        self._view.unsetCursor()
        return False

    def _handle_mouse_move(self, event: QMouseEvent) -> bool:
        scene_position = self._view.mapToScene(event.position().toPoint())
        local_position = self._view.image.mapFromScene(scene_position)

        boundary = self._view.image.pixmap().rect()
        if boundary.contains(local_position.toPoint()):
            self._update_highlight(scene_position)
        else:
            self._remove_highlight()

        return False

    def _handle_mouse_release(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._inspect(event)

        return False

    @Slot()
    def _handle_context_menu(self, menu: QMenu):
        for exporter in self._exporters:
            action = QAction(f"Export to {exporter.label}", self)
            action.triggered.connect(lambda _, it=exporter: self._export_selection(it))
            action.setEnabled(bool(self._points))
            menu.addAction(action)

    def _export_selection(self, exporter: Exporter):
        hypercube = self._container.hypercube
        spectra = hypercube.read_pixels([(p.y(), p.x()) for p in self._points])
        exporter.export(hypercube.name, spectra, hypercube.wavelengths)

    def _inspect(self, event: QMouseEvent):
        scene_position = self._view.mapToScene(event.position().toPoint())
        local_position = self._view.image.mapFromScene(scene_position)

        boundary = self._view.image.pixmap().rect()
        if not boundary.contains(local_position.toPoint()):
            self._points.clear()
            self._remove_crosshair()
            self.pixelCleared.emit()
            return

        point = QPoint(
            int(local_position.x()),
            int(local_position.y()),
        )

        if point in self._points:
            return

        multiple = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        if not multiple:
            self.pixelCleared.emit()
            self._remove_crosshair()
            self._points.clear()

        self._append_crosshair(point, get_color(len(self._points)))
        self._points.append(point)
        self.pixelClicked.emit(point)

    def _update_highlight(self, point):
        if self._highlight is None:
            self._highlight = PixelHighlight()
            self._view.scene().addItem(self._highlight)

        self._highlight.setRect(
            int(point.x()), int(point.y()), 1, 1,
        )

    def _remove_highlight(self):
        if self._highlight is not None:
            self._view.scene().removeItem(self._highlight)
            self._highlight = None

    def _append_crosshair(self, point, color):
        crosshair = PointHighlight(self._view, point, color)
        self._crosshair.append(crosshair)
        self._view.scene().addItem(crosshair)

    def _remove_crosshair(self):
        for item in self._crosshair:
            self._view.scene().removeItem(item)

        self._crosshair.clear()
