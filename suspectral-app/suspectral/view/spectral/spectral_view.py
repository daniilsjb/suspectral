import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QMenu, QWidget

from suspectral.colors import get_color
from suspectral.model.hypercube_container import HypercubeContainer


class SpectralView(pg.PlotWidget):
    """
    Widget for displaying spectral data using PyQtGraph.

    This widget visualizes 1D spectral profiles. It supports plotting spectra
    either against wavelength values or band indices. It allows dynamic updates,
    clearing of plots, and emits a signal for a custom context menu.

    Signals
    -------
    contextMenuRequested(menu: QMenu)
        Emitted when a context menu is requested and spectra are present.
        External components can connect to this signal to populate this menu.

    Parameters
    ----------
    model : HypercubeContainer
        The data model containing the spectral data.
    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    contextMenuRequested = Signal(QMenu)

    def __init__(self, *,
                 model: HypercubeContainer,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._model = model

        self._spectra: list[np.ndarray] = []
        self._wavelengths: np.ndarray | None = None

        self.getViewBox().setMenuEnabled(False)
        self.getViewBox().setMouseEnabled(x=False, y=False)
        self.getPlotItem().setContentsMargins(10, 20, 20, 10)

        self.setLabel("left", "Intensity")
        self.setLabel("bottom", "Wavelength")

        self.setMinimumWidth(400)
        self.setMinimumHeight(300)

    @Slot()
    def set_wavelengths(self, wavelengths: np.ndarray, unit: str | None = None):
        """
        Set the x-axis to use specified wavelength values.

        Parameters
        ----------
        wavelengths : np.ndarray
            Array of wavelength values corresponding to spectral bands.
        unit : str, optional
            Unit of the wavelength values (e.g., 'nm', 'µm'). If provided,
            it is included in the x-axis label.
        """
        self._wavelengths = wavelengths
        self.setXRange(wavelengths.min(), wavelengths.max())
        self.setLabel("bottom", f"Wavelength ({unit})" if unit else "Wavelength", unit=unit)

    @Slot()
    def set_band_numbers(self, num_bands: int):
        """
        Set the x-axis to display band indices instead of wavelengths.

        Parameters
        ----------
        num_bands : int
            The total number of spectral bands.
        """
        self._wavelengths = None
        self.setXRange(0, num_bands)
        self.setLabel("bottom", f"Band Number")

    @Slot()
    def add_spectrum(self, spectrum: np.ndarray):
        """
        Add a single spectrum to the plot.

        Parameters
        ----------
        spectrum : np.ndarray
            1D array containing spectral intensity values.
        """
        pen = pg.mkPen(get_color(len(self._spectra)))
        self.plot(x=self._wavelengths, y=spectrum, pen=pen, antialias=True)
        self._spectra.append(spectrum)

    @Slot()
    def clear_spectra(self):
        """Remove all spectra from the plot."""
        self.clear()
        self._spectra.clear()

    @Slot()
    def reset(self):
        """Reset the plot view to its initial state."""
        self.clear_spectra()
        self.setYRange(0, 1)
        self.setXRange(0, 1)
        self.getPlotItem().enableAutoRange(True, True)
        self.setLabel("bottom", "Wavelength")
        self._wavelengths = None

    @property
    def spectra(self) -> np.ndarray:
        """List of spectra currently displayed."""
        return np.array(self._spectra)

    @property
    def wavelengths(self) -> np.ndarray | None:
        """Current wavelength values used for the x-axis."""
        return self._wavelengths

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self._spectra:
            menu = QMenu(self)
            self.contextMenuRequested.emit(menu)
            menu.exec(event.globalPos())
