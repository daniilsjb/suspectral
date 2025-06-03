from PySide6.QtCore import QObject, Slot

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.metadata.metadata_view import MetadataView


class MetadataController(QObject):
    """
    Controller which synchronizes the metadata view with the currently opened hypercube.

    Parameters
    ----------
    view : MetadataView
        The metadata view to update.
    model : HypercubeContainer
        The model that manages hypercube loading and closing.
    parent : QObject or None, optional
        The parent object of the controller, by default None.
    """

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
