import numpy as np
from PySide6.QtCore import QObject, Slot, QPoint

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.manager import ToolManager
from suspectral.view.spectral_view import SpectralView


class SpectralController(QObject):
    def __init__(self, *,
                 view: SpectralView,
                 tools: ToolManager,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._model = model

        model.opened.connect(self._handle_hypercube_opened)
        model.closed.connect(self._handle_hypercube_closed)

        tools.toolChanged.connect(self._handle_tool_changed)

        tools.inspect.pixelClicked.connect(self._handle_pixel_clicked)
        tools.inspect.pixelCleared.connect(self._handle_pixel_cleared)

        tools.area.selectionMoved.connect(self._handle_selection_changed)
        tools.area.selectionEnded.connect(self._handle_selection_changed)
        tools.area.selectionSampled.connect(self._handle_selection_sampled)

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        if hypercube.wavelengths is None:
            self._view.set_bands(hypercube.num_bands)
            return

        self._view.set_wavelengths(
            hypercube.wavelengths,
            hypercube.wavelengths_unit,
        )

    @Slot()
    def _handle_hypercube_closed(self):
        self._view.reset()

    @Slot()
    def _handle_tool_changed(self):
        self._view.clear_spectra()

    @Slot()
    def _handle_pixel_clicked(self, point: QPoint):
        spectrum = self._model.hypercube.read_pixel(point.y(), point.x())
        self._view.add_spectrum(spectrum)

    @Slot()
    def _handle_pixel_cleared(self):
        self._view.clear_spectra()

    @Slot()
    def _handle_selection_changed(self):
        self._view.clear_spectra()

    @Slot()
    def _handle_selection_sampled(self, xs: np.ndarray, ys: np.ndarray):
        spectra = self._model.hypercube.read_subimage(ys, xs)
        spectra = spectra.reshape(-1, spectra.shape[-1])
        for spectrum in spectra:
            self._view.add_spectrum(spectrum)
