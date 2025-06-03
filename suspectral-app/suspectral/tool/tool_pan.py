from PySide6.QtWidgets import QGraphicsView

from suspectral.tool.tool import Tool


class PanTool(Tool):
    """
    Tool for panning within the image view using mouse drag.
    """

    def activate(self):
        self._view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().activate()

    def deactivate(self):
        self._view.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().deactivate()
