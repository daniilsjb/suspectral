import numpy as np
from PySide6.QtCore import Slot, QObject, Signal
from scipy.integrate import simpson
from scipy.interpolate import CubicSpline

from suspectral.model.hypercube import Hypercube


class SynthesizerCIE(QObject):
    """
    Synthesizes a color image from a hyperspectral cube using CIE color matching functions.

    This class transforms spectral data into RGB images by numerically integrating spectral
    reflectance with CIE 1931 color matching functions (CMFs), optionally modulated by a
    spectral power distribution (SPD) and normalized against white/black references.

    It supports optional post-processing steps including sRGB conversion, gamma correction,
    and contrast normalization. The process can be run asynchronously and interrupted.

    Signals
    -------
    progress(int)
        Emitted to indicate synthesis progress in percent (0–100).
    produced(np.ndarray)
        Emitted when the synthesis completes successfully with the resulting RGB image.
    finished()
        Emitted when the process has ended, regardless of whether it was completed or interrupted.

    Parameters
    ----------
    cmf : np.ndarray
        A structured array containing columns "Wavelength", "X", "Y", and "Z" for the
        color matching functions (typically from CIE 1931).
    hypercube : Hypercube
        The hyperspectral data cube to process.
    apply_srgb_transform : bool, optional
        Whether to convert XYZ to sRGB using the standard transformation matrix.
    apply_gamma_encoding : bool, optional
        Whether to apply sRGB gamma encoding after sRGB conversion.
    apply_per_channel_contrast : bool, optional
        Whether to normalize contrast individually per channel.
    white_ref : np.ndarray, optional
        A spectral reference used for white normalization.
    black_ref : np.ndarray, optional
        A spectral reference used for black normalization.
    spd : np.ndarray, optional
        A structured array with columns "Wavelength" and "Intensity" representing the
        spectral power distribution of the illuminant (e.g., D65). If not provided, a
        flat (equal energy) SPD is assumed.
    """

    progress = Signal(int)
    produced = Signal(np.ndarray)
    finished = Signal()

    def __init__(self,
                 cmf: np.ndarray,
                 hypercube: Hypercube,
                 apply_srgb_transform: bool = False,
                 apply_gamma_encoding: bool = False,
                 apply_per_channel_contrast: bool = False,
                 white_ref: np.ndarray | None = None,
                 black_ref: np.ndarray | None = None,
                 spd: np.ndarray | None = None):
        super().__init__()
        self._running = True
        self._hypercube = hypercube
        self._apply_srgb_transform = apply_srgb_transform
        self._apply_gamma_encoding = apply_gamma_encoding
        self._apply_per_channel_contrast = apply_per_channel_contrast

        # Ensure that hypercube's wavelengths intersect with CMFs.
        wavelengths = hypercube.wavelengths
        wavelengths_min = max(wavelengths.min(), cmf["Wavelength"].min())
        wavelengths_max = min(wavelengths.max(), cmf["Wavelength"].max())
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

        # Align CMFs with hypercube wavelengths.
        self._cmf_x = CubicSpline(cmf["Wavelength"], cmf["X"])(wavelengths)
        self._cmf_y = CubicSpline(cmf["Wavelength"], cmf["Y"])(wavelengths)
        self._cmf_z = CubicSpline(cmf["Wavelength"], cmf["Z"])(wavelengths)

        # Rescale CMFs to balance out the color sensitivities.
        k = simpson(self._cmf_y * self._spd, wavelengths)
        for cmf in (self._cmf_x, self._cmf_y, self._cmf_z):
            cmf /= k

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
            spectra = spectra[:, :, self._mask].astype(np.float64)

            # Make the darkest pixels appear black (optional).
            if self._black_ref is not None:
                spectra -= self._black_ref
                spectra[spectra < 0] = 0

            # Make the brightest pixels appear white (optional).
            if self._white_ref is not None:
                spectra /= self._white_ref
                spectra[spectra > 1] = 1

            # Sum up the contributions of the image components for this row.
            image[row, :, 0] = simpson(spectra * self._cmf_x * self._spd, w)
            image[row, :, 1] = simpson(spectra * self._cmf_y * self._spd, w)
            image[row, :, 2] = simpson(spectra * self._cmf_z * self._spd, w)
            self.progress.emit(int(row / (num_rows - 1) * 100))
        else:
            if self._apply_srgb_transform:
                # Apply the standard XYZ to sRGB transformation matrix.
                image = image.reshape(-1, 3).T
                image = np.array([
                    [+3.2404542, -1.5371385, -0.4985314],
                    [-0.9692660, +1.8760108, +0.0415560],
                    [+0.0556434, -0.2040259, +1.0572252],
                ]) @ image

                image = image.T.reshape((num_rows, num_cols, 3))

            # Apply contrast (either per-channel or globally).
            if self._apply_per_channel_contrast:
                image -= image.min(axis=(0, 1), keepdims=True)
                image /= image.max(axis=(0, 1), keepdims=True)
            else:
                image -= image.min()
                image /= image.max()

            # Apply the standard sRGB gamma encoding function.
            if self._apply_gamma_encoding:
                gamma_map = image <= 0.0031308
                image[ gamma_map] = 12.92 * image[ gamma_map]
                image[~gamma_map] = 1.055 * image[~gamma_map]**0.416 - 0.055

            # Emit the image for display.
            self.produced.emit(image)

        # Notify other threads of completion.
        self.finished.emit()

    @Slot()
    def stop(self):
        """Requests that the synthesis process ends early."""
        self._running = False
