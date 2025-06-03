from PySide6.QtCore import QObject, Slot, QPoint, QRect

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.manager import ToolManager
from suspectral.view.image.image_view import ImageView
from suspectral.view.status.status_view import StatusView


class StatusController(QObject):
    """
    Controller which synchronizes the status view with image view, tools, and hypercube model.

    Parameters
    ----------
    view : StatusView
        The status view widget to update.
    image : ImageView
        The image view emitting cursor position signals.
    tools : ToolManager
        The tool manager providing selection signals.
    model : HypercubeContainer
        The hypercube container model emitting opened and closed signals.
    parent : QObject or None, optional
        The parent object of the controller, by default None.
    """

    def __init__(self, *,
                 view: StatusView,
                 image: ImageView,
                 tools: ToolManager,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._model = model
        self._tools = tools

        model.opened.connect(self._handle_hypercube_opened)
        model.closed.connect(self._handle_hypercube_closed)

        tools.area.selectionMoved.connect(self._handle_selection_moved)
        tools.area.selectionEnded.connect(self._handle_selection_ended)

        image.cursorMovedInside.connect(self._handle_cursor_inside)
        image.cursorMovedOutside.connect(self._handle_cursor_outside)

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        self._view.update_hypercube(hypercube)

    @Slot()
    def _handle_hypercube_closed(self):
        self._view.clear()

    @Slot()
    def _handle_selection_moved(self, selection: QRect):
        self._view.update_selection(selection)

    @Slot()
    def _handle_selection_ended(self):
        self._view.clear_selection()

    @Slot()
    def _handle_cursor_inside(self, point: QPoint):
        self._view.update_cursor(point)

    @Slot()
    def _handle_cursor_outside(self):
        self._view.clear_cursor()
