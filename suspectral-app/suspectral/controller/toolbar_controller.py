from PySide6.QtCore import QObject, Slot

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.toolbar.toolbar_view import ToolbarView


class ToolbarController(QObject):
    """
    Controller which synchronizes the toolbar with the hypercube model.

    Parameters
    ----------
    view : ToolbarView
        The toolbar view to control.
    model : HypercubeContainer
        The hypercube container model emitting opened and closed signals.
    parent : QObject or None, optional
        The parent object of the controller, by default None.
    """

    def __init__(self, *,
                 view: ToolbarView,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._model = model

        model.opened.connect(self._handle_hypercube_opened)
        model.closed.connect(self._handle_hypercube_closed)

    @Slot()
    def _handle_hypercube_opened(self):
        self._view.setEnabled(True)

    @Slot()
    def _handle_hypercube_closed(self):
        self._view.setEnabled(False)
