import itertools
import numpy as np
from PySide6.QtCore import QObject, Slot, QPoint

from suspectral.hypercube.hypercube_container import HypercubeContainer
from suspectral.selection.selection_view import SelectionView


class SelectionController(QObject):
    def __init__(self,
                 view: SelectionView,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._model = model

        model.opened.connect(self._handle_opened)
        model.closed.connect(self._handle_closed)

    @Slot()
    def _handle_opened(self):
        self._view.clear()

    @Slot()
    def _handle_closed(self):
        self._view.clear()

    @Slot()
    def handle_tool_changed(self):
        self._view.clear()

    @Slot()
    def handle_pixel_clicked(self, point: QPoint):
        self._view.add_point(point)

    @Slot()
    def handle_pixel_cleared(self):
        self._view.clear()

    @Slot()
    def handle_selection_updated(self):
        self._view.clear()

    @Slot()
    def handle_selection_sampled(self, xs: np.ndarray, ys: np.ndarray):
        points = [QPoint(x, y) for x, y in itertools.product(xs, ys)]
        self._view.add_points(points)
