import numpy as np
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QApplication

from suspectral.exporter.exporter import Exporter


class CsvExporter(Exporter):
    def __init__(self):
        super().__init__("CSV")

    def export(self, name: str, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        downloads = QStandardPaths \
            .writableLocation(QStandardPaths.StandardLocation.DownloadLocation)

        path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            caption="Save File",
            filter="CSV (*.csv *.tsv)",
            dir = f"{downloads}/{name}.csv",
        )

        if not path: return

        if wavelengths is None:
            dat = spectra.T
            fmt = ["%.18e"] * spectra.shape[0]
        else:
            dat = np.column_stack((wavelengths.T, spectra.T))
            fmt = ["%g"] + ["%.18e"] * spectra.shape[0]

        np.savetxt(path, dat, delimiter="\t", fmt=fmt)
