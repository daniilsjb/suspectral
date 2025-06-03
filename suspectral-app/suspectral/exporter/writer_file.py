from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QApplication

from suspectral.exporter.writer import Writer


class FileWriter(Writer):
    """
    Writer that saves formatted spectral data to a user-selected file.

    Parameters
    ----------
    suffix : str
        The default file extension suffix to append to the suggested filename.
    filters : str
        The file type filters to apply in the save file dialog (e.g., "CSV (*.csv)").
    """

    def __init__(self, suffix: str, filters: str):
        self._suffix = suffix
        self._filter = filters

    def write(self, name: str, data: str | bytes):
        """
        Prompt the user to select a file location and save the data.

        Parameters
        ----------
        name : str
            The base name suggested for the saved file (without extension).
        data : str or bytes
            The formatted spectral data to save. If bytes, the file is opened in binary mode.
        """
        # By default, we will suggest saving the file in the system's "Downloads".
        downloads = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation
        )

        path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            caption="Save File",
            filter=self._filter,
            dir=f"{downloads}/{name}{self._suffix}",
        )

        if not path: return

        mode = "wb" if isinstance(data, bytes) else "w"
        with open(path, mode) as f:
            f.write(data)
