import numpy as np
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QApplication

from suspectral.exporter.exporter import Exporter


class CsvExporter(Exporter):
    def __init__(self):
        super().__init__("CSV")

    def export(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        downloads = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        file_path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            caption="Save File",
            filter="CSV (*.csv *.tsv)",
            dir = f"{downloads}/Spectra.csv",
        )

        if file_path:
            data = spectra.T
            fmt = ["%.18e"] * spectra.shape[0]

            if wavelengths is not None:
                data = np.column_stack((wavelengths.T, data))
                fmt.insert(0, "%g")

            np.savetxt(file_path, data, delimiter="\t", fmt=fmt)
