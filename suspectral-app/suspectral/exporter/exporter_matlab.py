import numpy as np
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QApplication
from scipy.io import savemat

from suspectral.exporter.exporter import Exporter


class MatlabExporter(Exporter):
    def __init__(self):
        super().__init__("MATLAB")

    def export(self, name: str, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        downloads = QStandardPaths \
            .writableLocation(QStandardPaths.StandardLocation.DownloadLocation)

        path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            caption="Save File",
            filter="MATLAB (*.mat)",
            dir=f"{downloads}/{name}.mat",
        )

        if not path: return
        savemat(path, {
            "wavelengths": wavelengths,
            "spectra": spectra,
        })
