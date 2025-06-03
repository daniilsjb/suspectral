from abc import ABC, abstractmethod

import numpy as np


class Formatter(ABC):
    """Abstract base class for formatting spectral data for export."""

    @abstractmethod
    def format(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None) -> str | bytes:
        """Format spectral data and optional wavelengths.

        Parameters
        ----------
        spectra : np.ndarray of shape (number of samples, number of bands)
            Spectral values for the pixel samples.

        wavelengths : np.ndarray of shape (numer of bands,), optional
            The wavelengths corresponding to the spectral bands, if available.

        Returns
        -------
        str or bytes
            A serialized representation of the data.
        """
        ...
