import numpy as np
from PySide6.QtWidgets import QWidget

from suspectral.view.status.status_view_item import StatusViewItem
from suspectral.theme_pixmap import ThemePixmap


class WavelengthStatus(StatusViewItem):
    """
    A widget that displays the wavelength range and step size of spectral data.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget, if any.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("wave.svg"), parent)

    def set(self, wavelengths: np.ndarray, wavelengths_unit: str | None = None):
        """
        Update the displayed wavelength range and step size.

        Parameters
        ----------
        wavelengths : np.ndarray of shape (number of bands,)
            Array of wavelength values.

        wavelengths_unit : str, optional
            Unit of the wavelengths (e.g., "nm", "µm"). If provided, it will
            be shown alongside the values.
        """
        unit = f" ({wavelengths_unit})" if wavelengths_unit else ""
        diff = np.round(np.diff(wavelengths), 2)
        step = f" : {diff[0]:g}" if np.all(diff == diff[0]) else ""

        wave_min = np.round(wavelengths.min(), 2)
        wave_max = np.round(wavelengths.max(), 2)

        self._label.setText(f"{wave_min:g} : {wave_max:g}{step}{unit}")
