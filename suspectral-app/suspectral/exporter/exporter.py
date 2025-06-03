import numpy as np

from suspectral.exporter.formatter import Formatter
from suspectral.exporter.writer import Writer


class Exporter:
    """
    Combines a data formatter and writer to export spectral data using a specified format and destination.

    Parameters
    ----------
    label : str
        A human-readable label describing the exporter (e.g., "CSV", "MATLAB").
    writer : Writer
        The writer instance responsible for outputting the serialized data (e.g., to file or clipboard).
    formatter : Formatter
        The formatter instance responsible for converting the spectra (and, optionally, wavelengths) to
        a string or byte representation.
    """

    def __init__(self, label: str, writer: Writer, formatter: Formatter):
        self.label = label
        self._writer = writer
        self._formatter = formatter

    def export(self, name: str, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        """
        Formats and exports spectral data to the configured destination.

        Parameters
        ----------
        name : str
            The display-friendly name used for saving the file or labeling the output, if applicable.
        spectra : np.ndarray of shape (bands, samples)
            The spectral data, where each column represents a spectrum for a single pixel or sample.
        wavelengths : np.ndarray of shape (bands,), optional
            The wavelength values corresponding to each spectral band. If provided, it may be included
            in the export, depending on the formatter.
        """
        self._writer.write(name, self._formatter.format(spectra, wavelengths))
