from PySide6.QtCore import QObject, Signal

from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.tool import Tool
from suspectral.tool.tool_area import AreaTool
from suspectral.tool.tool_drag import DragTool
from suspectral.tool.tool_inspect import InspectTool
from suspectral.tool.tool_none import NoneTool
from suspectral.tool.tool_zoom import ZoomTool
from suspectral.view.image.image_view import ImageView


class ToolManager(QObject):
    toolChanged = Signal()

    def __init__(self, *,
                 view: ImageView,
                 model: HypercubeContainer,
                 exporters: list[Exporter],
                 parent: QObject | None = None):
        super().__init__(parent)

        self._view = view
        self._model = model

        self._none = NoneTool(view)
        self._drag = DragTool(view)
        self._zoom = ZoomTool(view)
        self._area = AreaTool(view, model, exporters)
        self._inspect = InspectTool(view, model, exporters)

        self._active_tool = self._none
        self._model.opened.connect(lambda: self._active_tool.activate())
        self._model.closed.connect(lambda: self._active_tool.deactivate())

    def set(self, tool: Tool):
        if self._active_tool is not tool:
            self._active_tool.deactivate()
            self._active_tool = tool
            self._active_tool.activate()
            self.toolChanged.emit()

    @property
    def none(self) -> NoneTool:
        return self._none

    @property
    def drag(self) -> DragTool:
        return self._drag

    @property
    def zoom(self) -> ZoomTool:
        return self._zoom

    @property
    def area(self) -> AreaTool:
        return self._area

    @property
    def inspect(self) -> InspectTool:
        return self._inspect
