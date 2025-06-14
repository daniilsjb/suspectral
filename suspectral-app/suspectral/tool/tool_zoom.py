from typing import cast

from PySide6.QtCore import QEvent, Qt, QObject
from PySide6.QtGui import QMouseEvent, QCursor, QPixmap

from suspectral.view.image.image_view import ImageView
from suspectral.tool.tool import Tool


class ZoomTool(Tool):
    """
    Tool for interactive zooming within the image view.

    This tool modifies the cursor to a magnifier icon and enables the user to zoom
    in or out by clicking on the image. Left-click zooms in, and right-click zooms out.
    It also filters out context menu events and manages cursor visibility when entering
    or leaving the image area.

    Parameters
    ----------
    view : ImageView
        The image view where zooming operations will be applied.
    parent : QObject or None, optional
        The parent object of the tool, by default None.
    """

    def __init__(self, view: ImageView, parent: QObject | None = None):
        super().__init__(view, parent)
        self._cursor = QCursor(QPixmap(":/icons/magnifier-left.png"))

    def deactivate(self):
        self._view.unsetCursor()
        super().deactivate()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Enter:
            return self._handle_enter(event)
        elif event.type() == QEvent.Type.Leave:
            return self._handle_leave(event)
        elif event.type() == QEvent.Type.ContextMenu:
            return self._handle_context_menu(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            return self._handle_mouse_release(cast(QMouseEvent, event))

        return super().eventFilter(watched, event)

    def _handle_enter(self, _: QEvent) -> bool:
        self._view.setCursor(self._cursor)
        return False

    def _handle_leave(self, _: QEvent) -> bool:
        self._view.unsetCursor()
        return False

    @staticmethod
    def _handle_context_menu(_: QEvent) -> bool:
        # Context menu requests are filtered out in zooming image.
        return True

    def _handle_mouse_release(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton:
            self._view.zoom_in(2.0)
        elif event.button() == Qt.MouseButton.RightButton:
            self._view.zoom_out(2.0)

        return False
