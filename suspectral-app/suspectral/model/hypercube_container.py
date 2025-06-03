from PySide6.QtCore import QObject, Signal

from suspectral.model.hypercube import Hypercube


class HypercubeContainer(QObject):
    """
    Manages the lifecycle of a Hypercube instance, observable via signals.

    Signals
    -------
    opened : Signal
        Emitted with the opened `Hypercube` instance when a hypercube is successfully opened.
    closed : Signal
        Emitted when the current hypercube is closed.
    """

    opened = Signal(Hypercube)
    closed = Signal()

    def __init__(self):
        super().__init__()
        self._hypercube: Hypercube | None = None

    def open(self, path: str) -> Hypercube:
        """
        Open a hypercube from the given file path.

        If another hypercube is already open, it will be closed first.

        Parameters
        ----------
        path : str
            Path to the ENVI header file.

        Returns
        -------
        Hypercube
            The newly opened Hypercube instance.
        """
        if self._hypercube is not None:
            self.close()

        self._hypercube = Hypercube(path)
        self.opened.emit(self._hypercube)
        return self._hypercube

    def close(self):
        """Close the currently opened hypercube, if any, and emit the `closed` signal."""
        del self._hypercube
        self._hypercube = None
        self.closed.emit()

    @property
    def hypercube(self) -> Hypercube | None:
        """The currently opened Hypercube instance, or None if no hypercube is opened."""
        return self._hypercube
