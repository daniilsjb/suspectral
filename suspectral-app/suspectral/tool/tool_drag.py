from PySide6.QtWidgets import QGraphicsView

from suspectral.tool.tool import Tool


class DragTool(Tool):
    def activate(self):
        self._view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().activate()

    def deactivate(self):
        self._view.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().deactivate()
