from PySide6.QtWidgets import QApplication

from suspectral.exporter.writer import Writer


class ClipboardWriter(Writer):
    """Writer that copies formatted spectral data to the system clipboard."""

    def write(self, name: str, data: str):
        """Copy data to the system clipboard.

        Parameters
        ----------
        name : str
            The base name of the export (not used in this implementation).

        data : str
            The formatted spectral data to copy. This method expects a string;
            if bytes are provided, they should be decoded before passing.
        """
        QApplication.clipboard().setText(data)
