from PySide6.QtCore import QObject, Signal

from suspectral.model.hypercube import Hypercube


class HypercubeContainer(QObject):
    opened = Signal(Hypercube)
    closed = Signal()

    def __init__(self):
        super().__init__()
        self._hypercube: Hypercube | None = None

    def open(self, path: str) -> Hypercube:
        if self._hypercube is not None:
            self.close()

        self._hypercube = Hypercube(path)
        self.opened.emit(self._hypercube)
        return self._hypercube

    def close(self):
        self._hypercube = None
        self.closed.emit()

    @property
    def hypercube(self) -> Hypercube | None:
        return self._hypercube
