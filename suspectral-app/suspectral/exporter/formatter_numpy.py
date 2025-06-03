import io

import numpy as np

from suspectral.exporter.formatter import Formatter


class NpyFormatter(Formatter):
    """Formatter that serializes spectral data into NumPy `.npy` format."""

    def format(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None) -> bytes:
        """Format spectral data and optional wavelengths as a NumPy `.npy` file.

        Parameters
        ----------
        spectra : np.ndarray of shape (number of samples, number of bands)
            Spectral values for the pixel samples.

        wavelengths : np.ndarray of shape (number of bands,), optional
            The wavelengths corresponding to the spectral bands. If provided,
            they will be prepended as the first row in the output array.

        Returns
        -------
        bytes
            A binary-encoded NumPy (`.npy`) file. The resulting array has shape
            (number of samples + 1, number of bands) if wavelengths are included,
            or (number of samples, number of bands) otherwise.
        """
        buffer = io.BytesIO()

        if wavelengths is not None:
            np.save(buffer, np.vstack((wavelengths, spectra)))
        else:
            np.save(buffer, spectra)

        return buffer.getvalue()
