import io

import numpy as np
from scipy.io import savemat

from suspectral.exporter.formatter import Formatter


class MatlabFormatter(Formatter):
    """Formatter that serializes spectral data into MATLAB `.mat` binary format."""

    def format(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None) -> bytes:
        """Format spectral data and optional wavelengths as a MATLAB `.mat` file.

        Parameters
        ----------
        spectra : np.ndarray of shape (number of samples, number of bands)
            Spectral values for the pixel samples.

        wavelengths : np.ndarray of shape (number of bands,), optional
            The wavelengths corresponding to the spectral bands. If provided,
            they will be included in the output under the key 'wavelengths'.

        Returns
        -------
        bytes
            A binary-encoded MATLAB (`.mat`) file. The resulting structure contains
            two arrays: 'spectra' and, if given, 'wavelengths'.
        """
        buffer = io.BytesIO()
        if wavelengths is not None:
            savemat(buffer, {"spectra": spectra, "wavelengths": wavelengths})
        else:
            savemat(buffer, {"spectra": spectra})

        return buffer.getvalue()
