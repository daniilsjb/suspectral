from PySide6.QtCore import QObject, Slot

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.metadata_view import MetadataView


class MetadataController(QObject):
    def __init__(self, *,
                 view: MetadataView,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._model = model
        self._view = view

        model.opened.connect(self._handle_hypercube_opened)
        model.closed.connect(self._handle_hypercube_closed)

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        self._view.set(hypercube.metadata)

    @Slot()
    def _handle_hypercube_closed(self):
        self._view.clear()
