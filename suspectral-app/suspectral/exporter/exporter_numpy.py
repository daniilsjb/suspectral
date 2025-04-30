import numpy as np
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QApplication

from suspectral.exporter.exporter import Exporter


class NpyExporter(Exporter):
    def __init__(self):
        super().__init__("NPy")

    def export(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        downloads = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        file_path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            caption="Save File",
            filter="NumPy Array (*.npy)",
            dir=f"{downloads}/Spectra.npy"
        )

        if file_path:
            data = spectra
            if wavelengths is not None:
                data = np.vstack((wavelengths, data))

            with open(file_path, "wb") as file:
                np.save(file, data)
