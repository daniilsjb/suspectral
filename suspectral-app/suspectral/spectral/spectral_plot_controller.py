import numpy as np
from PySide6.QtCore import QObject, Slot, QPoint

from suspectral.hypercube.hypercube import Hypercube
from suspectral.hypercube.hypercube_container import HypercubeContainer
from suspectral.spectral.spectral_plot_view import SpectralPlotView


class SpectralPlotController(QObject):
    def __init__(self,
                 view: SpectralPlotView,
                 model: HypercubeContainer,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._model = model

        model.opened.connect(self._handle_opened)
        model.closed.connect(self._handle_closed)

    @Slot()
    def _handle_opened(self, hypercube: Hypercube):
        if hypercube.wavelengths is None:
            self._view.set_band_numbers(hypercube.num_bands)
            return

        self._view.set_wavelengths(
            hypercube.wavelengths,
            hypercube.wavelengths_unit,
        )

    @Slot()
    def _handle_closed(self):
        self._view.reset()

    @Slot()
    def handle_tool_changed(self):
        self._view.clear_spectra()

    @Slot()
    def handle_pixel_clicked(self, point: QPoint):
        spectrum = self._model.hypercube.read_pixel(point.y(), point.x())
        self._view.add_spectrum(spectrum)

    @Slot()
    def handle_pixel_cleared(self):
        self._view.clear_spectra()

    @Slot()
    def handle_selection_updated(self):
        self._view.clear_spectra()

    @Slot()
    def handle_selection_sampled(self, xs: np.ndarray, ys: np.ndarray):
        spectra = self._model.hypercube.read_subimage(ys, xs)
        spectra = spectra.reshape(-1, spectra.shape[-1])
        for spectrum in spectra:
            self._view.add_spectrum(spectrum)
