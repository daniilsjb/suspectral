import io

import numpy as np

from suspectral.exporter.formatter import Formatter


class CsvFormatter(Formatter):
    """Formatter that serializes spectral data into tab-delimited CSV format."""

    def format(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None) -> str:
        """Format spectral data and optional wavelengths as CSV text.

        Parameters
        ----------
        spectra : np.ndarray of shape (number of samples, number of bands)
            Spectral values for the pixel samples.

        wavelengths : np.ndarray of shape (number of bands,), optional
            The wavelengths corresponding to the spectral bands. If provided, the output
            will include them as the first column.

        Returns
        -------
        str
            A UTF-8 encoded string in tab-delimited CSV format. Each row corresponds
            to a wavelength (or band), and each column (after the optional first)
            corresponds to a sample.
        """
        if wavelengths is None:
            dat = spectra.T
            fmt = ["%.18e"] * spectra.shape[0]
        else:
            dat = np.column_stack((wavelengths.T, spectra.T))
            fmt = ["%g"] + ["%.18e"] * spectra.shape[0]

        output = io.StringIO()
        np.savetxt(output, dat, delimiter="\t", fmt=fmt)
        return output.getvalue()
