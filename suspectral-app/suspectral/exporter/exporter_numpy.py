import numpy as np
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QApplication

from suspectral.exporter.exporter import Exporter


class NpyExporter(Exporter):
    def __init__(self):
        super().__init__("NPy")

    def export(self, name: str, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        downloads = QStandardPaths \
            .writableLocation(QStandardPaths.StandardLocation.DownloadLocation)

        path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            caption="Save File",
            filter="NumPy Array (*.npy)",
            dir=f"{downloads}/{name}.npy"
        )

        if not path: return

        if wavelengths is not None:
            data = np.vstack((wavelengths, spectra))
        else:
            data = spectra

        np.save(path, data)
