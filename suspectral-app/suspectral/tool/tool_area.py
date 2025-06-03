from typing import cast

import itertools
import numpy as np
from PySide6.QtCore import Signal, QPoint, QRect, QEvent, Qt, QPointF, QRectF, QObject, Slot
from PySide6.QtGui import QMouseEvent, QAction
from PySide6.QtWidgets import QMenu

from suspectral.colors import get_color
from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.highlight_area import AreaHighlight
from suspectral.tool.highlight_point import PointHighlight
from suspectral.tool.tool import Tool
from suspectral.view.image.image_view import ImageView


class AreaTool(Tool):
    """
    Tool to select and inspect rectangular areas within an image view.

    This tool allows the user to click and drag to select a rectangular region
    on the image. It visually highlights the selection area, provides sampling points,
    and supports exporting the spectral data within the selected region or sample points.

    Signals
    -------
    selectionStarted : QPointF
        Emitted when the user starts an area selection.
    selectionMoved : QRect
        Emitted when the selection rectangle changes during dragging.
    selectionStopped : QRect
        Emitted when the user finishes the selection drag.
    selectionSampled : np.ndarray, np.ndarray
        Emitted when sampling points within the selected area are computed.
    selectionEnded : None
        Emitted when the selection is reset or cleared.

    Parameters
    ----------
    view : ImageView
        The image view widget where interaction occurs.
    container : HypercubeContainer
        The hypercube model containing spectral data.
    exporters : list[Exporter]
        Exporters instances available for exporting selected pixel spectra.
    """

    selectionStarted = Signal(QPointF)
    selectionMoved = Signal(QRect)
    selectionStopped = Signal(QRect)
    selectionSampled = Signal(np.ndarray, np.ndarray)
    selectionEnded = Signal()

    def __init__(self, view: ImageView, container: HypercubeContainer, exporters: list[Exporter]):
        super().__init__(view)
        self._container = container
        self._exporters = exporters

        self._selecting = False
        self._selection_rect: QRect | None = None
        self._selection_source = QPoint()
        self._selection_target = QPoint()
        self._selection_moved = False

        self._highlight: AreaHighlight | None = None
        self._samples: list[PointHighlight] = []
        self._sample_xs: np.ndarray | None = None
        self._sample_ys: np.ndarray | None = None

    def activate(self):
        super().activate()
        self._view.contextMenuRequested.connect(self._handle_context_menu)

    def deactivate(self):
        self._view.contextMenuRequested.disconnect(self._handle_context_menu)
        self.selectionEnded.emit()
        self._reset()
        self._view.unsetCursor()
        super().deactivate()

    def _reset(self):
        self._selecting = False
        self._selection_source = QPoint()
        self._selection_target = QPoint()
        self._selection_moved = False
        self._remove_highlight()
        self._remove_samples()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Enter:
            return self._handle_enter(event)
        if event.type() == QEvent.Type.Leave:
            return self._handle_leave(event)
        if event.type() == QEvent.Type.MouseButtonPress:
            return self._handle_mouse_press(cast(QMouseEvent, event))
        if event.type() == QEvent.Type.MouseMove:
            return self._handle_mouse_move(cast(QMouseEvent, event))
        if event.type() == QEvent.Type.MouseButtonRelease:
            return self._handle_mouse_release(cast(QMouseEvent, event))

        return super().eventFilter(watched, event)

    def _handle_enter(self, _: QEvent) -> bool:
        self._view.setCursor(Qt.CursorShape.CrossCursor)
        return False

    def _handle_leave(self, _: QEvent) -> bool:
        self._view.unsetCursor()
        return False

    def _handle_mouse_press(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_selection(event)

        return False

    def _handle_mouse_move(self, event: QMouseEvent) -> bool:
        self._move_selection(event)
        return False

    def _handle_mouse_release(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton:
            self._stop_selection(event)

        return False

    @Slot()
    def _handle_context_menu(self, menu: QMenu):
        menu_area = menu.addMenu("Selection Area")
        for exporter in self._exporters:
            action = QAction(f"Export All to {exporter.label}", self)
            action.triggered.connect(lambda _, it=exporter: self._export_selection_area(it))
            action.setEnabled(bool(self._selection_rect))
            menu_area.addAction(action)

        menu_points = menu.addMenu("Selection Points")
        for exporter in self._exporters:
            action = QAction(f"Export to {exporter.label}", self)
            action.triggered.connect(lambda _, it=exporter: self._export_selection_points(it))
            action.setEnabled(bool(self._selection_rect))
            menu_points.addAction(action)

    def _export_selection_area(self, exporter: Exporter):
        tl = self._selection_rect.topLeft()
        br = self._selection_rect.bottomRight()

        hypercube = self._container.hypercube
        spectra = hypercube.read_subregion((tl.y(), br.y()), (tl.x(), br.x()))
        spectra = spectra.reshape(-1, spectra.shape[-1])

        exporter.export(hypercube.name, spectra, hypercube.wavelengths)

    def _export_selection_points(self, exporter: Exporter):
        hypercube = self._container.hypercube
        spectra = hypercube.read_pixels([(x, y) for y, x in itertools.product(self._sample_ys, self._sample_xs)])
        exporter.export(hypercube.name, spectra, hypercube.wavelengths)

    def _start_selection(self, event: QMouseEvent):
        point = self._get_center_point(event)
        self._selecting = True
        self._selection_source = point
        self.selectionStarted.emit(point)
        self._remove_samples()

    def _move_selection(self, event: QMouseEvent):
        if not self._selecting: return

        point = self._get_center_point(event)
        self._selection_moved = True
        self._selection_target = point

        self._selection_rect = self._get_selection_rect()
        self.selectionMoved.emit(self._selection_rect)
        self._update_highlight(self._selection_rect)

    def _stop_selection(self, event: QMouseEvent):
        if not self._selecting: return

        if not self._selection_moved:
            self._reset()
            self._selection_rect = None
            self.selectionEnded.emit()
            return

        point = self._get_center_point(event)
        self._selecting = False
        self._selection_moved = False
        self._selection_target = point

        self._selection_rect = self._get_selection_rect()
        self.selectionStopped.emit(self._selection_rect)
        self._update_highlight(self._selection_rect)
        self._sample_selection()

    def _sample_selection(self):
        tl = self._selection_rect.topLeft()
        br = self._selection_rect.bottomRight()

        self._sample_xs = np.unique(np.linspace(start=tl.x(), stop=br.x() - 1, num=3).astype(int))
        self._sample_ys = np.unique(np.linspace(start=tl.y(), stop=br.y() - 1, num=3).astype(int))

        for y, x in itertools.product(self._sample_ys, self._sample_xs):
            sample = PointHighlight(self._view, QPoint(x, y), get_color(len(self._samples)))
            self._samples.append(sample)
            self._view.scene().addItem(sample)

        self.selectionSampled.emit(self._sample_xs, self._sample_ys)

    def _update_highlight(self, rect):
        if self._highlight is None:
            self._highlight = AreaHighlight()
            self._view.scene().addItem(self._highlight)

        tl = self._view.image.mapToScene(rect.topLeft())
        br = self._view.image.mapToScene(rect.bottomRight())
        self._highlight.setRect(QRectF(tl, br))

    def _remove_highlight(self):
        if self._highlight is not None:
            self._view.scene().removeItem(self._highlight)
            self._highlight = None

    def _remove_samples(self):
        for sample in self._samples:
            self._view.scene().removeItem(sample)

        self._samples.clear()
        self._sample_xs = None
        self._sample_ys = None

    def _get_selection_rect(self):
        tlx = min(self._selection_source.x(), self._selection_target.x())
        tly = min(self._selection_source.y(), self._selection_target.y())

        brx = max(self._selection_source.x(), self._selection_target.x())
        bry = max(self._selection_source.y(), self._selection_target.y())

        return QRect(
            QPoint(tlx + 0, tly + 0),
            QPoint(brx + 1, bry + 1),
        )

    def _get_center_point(self, event: QMouseEvent):
        width = self._view.image.pixmap().width()
        height = self._view.image.pixmap().height()

        scene_position = self._view.mapToScene(event.position().toPoint())
        scene_position = QPointF(
            max(0.0, min(scene_position.x(), width - 1)),
            max(0.0, min(scene_position.y(), height - 1)),
        )

        point = self._view.image.mapFromScene(scene_position)
        return QPointF(
            int(point.x()) + 0.5,
            int(point.y()) + 0.5,
        )
