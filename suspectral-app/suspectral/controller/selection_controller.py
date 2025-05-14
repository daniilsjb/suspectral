import itertools
import numpy as np
from PySide6.QtCore import QObject, Slot, QPoint

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.manager import ToolManager
from suspectral.view.selection_view import SelectionView


class SelectionController(QObject):
    def __init__(self, *,
                 view: SelectionView,
                 tools: ToolManager,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._model = model
        self._tools = tools

        model.opened.connect(self._handle_hypercube_opened)
        model.closed.connect(self._handle_hypercube_closed)

        tools.toolChanged.connect(self._handle_tool_changed)

        tools.inspect.pixelClicked.connect(self._handle_pixel_clicked)
        tools.inspect.pixelCleared.connect(self._handle_pixel_cleared)

        tools.area.selectionMoved.connect(self._handle_selection_changed)
        tools.area.selectionEnded.connect(self._handle_selection_changed)
        tools.area.selectionSampled.connect(self._handle_selection_sampled)

    @Slot()
    def _handle_hypercube_opened(self):
        self._view.clear()

    @Slot()
    def _handle_hypercube_closed(self):
        self._view.clear()

    @Slot()
    def _handle_tool_changed(self):
        self._view.clear()

    @Slot()
    def _handle_selection_changed(self):
        self._view.clear()

    @Slot()
    def _handle_selection_sampled(self, xs: np.ndarray, ys: np.ndarray):
        self._view.add_points([QPoint(x, y) for x, y in itertools.product(xs, ys)])

    @Slot()
    def _handle_pixel_clicked(self, point: QPoint):
        self._view.add_point(point)

    @Slot()
    def _handle_pixel_cleared(self):
        self._view.clear()
