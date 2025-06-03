from PySide6.QtCore import QObject, Signal

from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.tool import Tool
from suspectral.tool.tool_area import AreaTool
from suspectral.tool.tool_pan import PanTool
from suspectral.tool.tool_inspect import InspectTool
from suspectral.tool.tool_none import NoneTool
from suspectral.tool.tool_zoom import ZoomTool
from suspectral.view.image.image_view import ImageView


class ToolManager(QObject):
    """
    Manages switching and lifecycle of interaction tools for the image view.

    Signals
    -------
    toolChanged : None
        Emitted whenever the active tool is changed.

    Parameters
    ----------
    view : ImageView
        The image view widget where interaction occurs.
    model : HypercubeContainer
        The hypercube model containing spectral data.
    exporters : list[Exporter]
        Exporters instances available for exporting selected pixel spectra.
    parent : QObject or None, optional
        The parent object, by default None.
    """

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
        self._pan = PanTool(view)
        self._zoom = ZoomTool(view)
        self._area = AreaTool(view, model, exporters)
        self._inspect = InspectTool(view, model, exporters)

        self._active_tool = self._none
        self._model.opened.connect(lambda: self._active_tool.activate())
        self._model.closed.connect(lambda: self._active_tool.deactivate())

    def set(self, tool: Tool):
        """
        Activate the given tool and deactivate the previously active tool.

        Parameters
        ----------
        tool : Tool
            The tool instance to activate.
        """
        if self._active_tool is not tool:
            self._active_tool.deactivate()
            self._active_tool = tool
            self._active_tool.activate()
            self.toolChanged.emit()

    @property
    def none(self) -> NoneTool:
        """The tool that disables interaction."""
        return self._none

    @property
    def pan(self) -> PanTool:
        """The tool for panning the image view."""
        return self._pan

    @property
    def zoom(self) -> ZoomTool:
        """The tool for zooming the image view."""
        return self._zoom

    @property
    def area(self) -> AreaTool:
        """The tool for selecting and inspecting rectangular areas."""
        return self._area

    @property
    def inspect(self) -> InspectTool:
        """The tool for pixel-level inspection and selection."""
        return self._inspect
