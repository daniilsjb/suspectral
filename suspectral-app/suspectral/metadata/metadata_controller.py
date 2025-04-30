from PySide6.QtCore import QObject, Slot

from suspectral.metadata.metadata_view import MetadataView
from suspectral.hypercube.hypercube import Hypercube
from suspectral.hypercube.hypercube_container import HypercubeContainer


class MetadataController(QObject):
    def __init__(self,
                 view: MetadataView,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._model = model
        self._view = view

        model.opened.connect(self._handle_opened)
        model.closed.connect(self._handle_closed)

    @Slot()
    def _handle_opened(self, hypercube: Hypercube):
        self._view.set_items(hypercube.metadata)

    @Slot()
    def _handle_closed(self):
        self._view.clear()
