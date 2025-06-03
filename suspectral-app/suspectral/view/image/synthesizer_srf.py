import numpy as np
from PySide6.QtCore import Slot, QObject, Signal
from scipy.integrate import simpson
from scipy.interpolate import CubicSpline

from suspectral.model.hypercube import Hypercube


class SynthesizerSRF(QObject):
    """
    Synthesizes a color image from a hyperspectral cube using sensor spectral response functions (SRFs).

    This class simulates RGB image acquisition from hyperspectral data by integrating each spectrum
    with pre-defined red, green, and blue spectral response functions. Optionally, the spectra can be
    normalized using black and white references, modulated by a spectral power distribution (SPD), and
    enhanced with contrast normalization.

    Signals
    -------
    progress(int)
        Emitted to report synthesis progress in percent (0–100).
    produced(np.ndarray)
        Emitted when the final RGB image has been successfully synthesized.
    finished()
        Emitted when the synthesis process has ended, whether normally or prematurely.

    Parameters
    ----------
    srf : np.ndarray
        A structured array containing the spectral response functions, with fields
        "Wavelength", "R", "G", and "B" corresponding to the red, green, and blue channels.
    hypercube : Hypercube
        The hyperspectral data cube to process.
    apply_per_channel_contrast : bool, optional
        Whether to normalize image contrast per channel after synthesis.
    white_ref : np.ndarray, optional
        A spectral reference used for white normalization.
    black_ref : np.ndarray, optional
        A spectral reference used for black normalization.
    spd : np.ndarray, optional
        A structured array with fields "Wavelength" and "Intensity" representing the
        spectral power distribution of the illuminant. If not provided, a flat spectrum
        (equal-energy, e.g., CIE E) is assumed.
    """

    progress = Signal(int)
    produced = Signal(np.ndarray)
    finished = Signal()

    def __init__(self,
                 srf: np.ndarray,
                 hypercube: Hypercube,
                 apply_per_channel_contrast: bool = False,
                 white_ref: np.ndarray | None = None,
                 black_ref: np.ndarray | None = None,
                 spd: np.ndarray | None = None):
        super().__init__()
        self._running = True
        self._hypercube = hypercube
        self._apply_per_channel_contrast = apply_per_channel_contrast

        # Ensure that hypercube's wavelengths intersect with SRFs.
        wavelengths = hypercube.wavelengths
        wavelengths_min = max(wavelengths.min(), srf["Wavelength"].min())
        wavelengths_max = min(wavelengths.max(), srf["Wavelength"].max())
        mask = ((wavelengths >= wavelengths_min) &
                (wavelengths <= wavelengths_max))
        wavelengths = wavelengths[mask]

        # Trim the white and black references; precompute the divisor.
        self._white_ref = white_ref[mask] if white_ref is not None else None
        self._black_ref = black_ref[mask] if black_ref is not None else None
        if black_ref is not None and white_ref is not None:
            self._white_ref -= self._black_ref

        # Align normalized SPD with the hypercube wavelengths.
        if spd is not None:
            spd_wavelengths = spd["Wavelength"]
            spd_intensities = spd["Intensity"]
            self._spd = spd_intensities / spd_intensities.max()
            self._spd = CubicSpline(spd_wavelengths, self._spd)(wavelengths)
        else:
            self._spd = 1.0  # Assume that CIE E is used by default.

        # Align SRFs with hypercube wavelengths.
        self._srf_r = CubicSpline(srf["Wavelength"], srf["R"])(wavelengths)
        self._srf_g = CubicSpline(srf["Wavelength"], srf["G"])(wavelengths)
        self._srf_b = CubicSpline(srf["Wavelength"], srf["B"])(wavelengths)

        # Rescale SRFs to balance out the color sensitivities.
        self._srf_r /= simpson(self._srf_r, wavelengths)
        self._srf_g /= simpson(self._srf_g, wavelengths)
        self._srf_b /= simpson(self._srf_b, wavelengths)

        self._mask = mask

    @Slot()
    def run(self):
        """Starts the spectral-to-RGB image synthesis."""
        # Load hypercube dimensions for convenience.
        num_rows = self._hypercube.num_rows
        num_cols = self._hypercube.num_cols

        # Load the integration argument from the hypercube.
        w = self._hypercube.wavelengths[self._mask]

        # Generate the image row-by-row (interruptable from other threads).
        image = np.zeros((num_rows, num_cols, 3))
        for row in range(num_rows):
            # Stop prematurely if requested; the image won't be produced.
            if not self._running: break

            # Load the next row of spectra from the hypercube.
            spectra = self._hypercube.read_row(row)
            spectra = spectra[:, :, self._mask]

            # Make the darkest pixels appear black (optional).
            if self._black_ref is not None:
                spectra -= self._black_ref
                spectra[spectra < 0] = 0

            # Make the brightest pixels appear white (optional).
            if self._white_ref is not None:
                spectra /= self._white_ref
                spectra[spectra > 1] = 1

            # Sum up the contributions of all the image components.
            image[row, :, 0] = simpson(spectra * self._srf_r * self._spd, w)
            image[row, :, 1] = simpson(spectra * self._srf_g * self._spd, w)
            image[row, :, 2] = simpson(spectra * self._srf_b * self._spd, w)

            # Emit a progress update in percents.
            self.progress.emit(int(row / (num_rows - 1) * 100))
        else:
            # Apply contrast (either per-channel or globally).
            if self._apply_per_channel_contrast:
                image -= image.min(axis=(0, 1), keepdims=True)
                image /= image.max(axis=(0, 1), keepdims=True)
            else:
                image -= image.min()
                image /= image.max()

            # Emit the image for display.
            self.produced.emit(image)

        # Notify other threads of completion.
        self.finished.emit()

    @Slot()
    def stop(self):
        """Requests that the synthesis process ends early."""
        self._running = False
