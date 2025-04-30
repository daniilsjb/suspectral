import numpy as np
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QApplication
from scipy.io import savemat

from suspectral.exporter.exporter import Exporter


class MatlabExporter(Exporter):
    def __init__(self):
        super().__init__("MATLAB")

    def export(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        downloads = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        file_path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            caption="Save File",
            filter="MATLAB (*.mat)",
            dir=f"{downloads}/Spectra.mat",
        )

        if file_path:
            savemat(file_path, {
                "wavelengths": wavelengths,
                "spectra": spectra,
            })
