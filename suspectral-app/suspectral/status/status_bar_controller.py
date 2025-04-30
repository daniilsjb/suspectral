from PySide6.QtCore import QObject, Slot

from suspectral.hypercube.hypercube import Hypercube
from suspectral.hypercube.hypercube_container import HypercubeContainer
from suspectral.status.status_bar import StatusBar


class StatusBarController(QObject):
    def __init__(self,
                 view: StatusBar,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._model = model
        self._view = view

        model.opened.connect(self._handle_opened)
        model.closed.connect(self._handle_closed)

    @Slot()
    def _handle_opened(self, hypercube: Hypercube):
        self._view.update_hypercube_status(hypercube)

    @Slot()
    def _handle_closed(self):
        self._view.clear()
