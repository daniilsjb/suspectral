import io

import numpy as np
from PySide6.QtWidgets import QApplication

from suspectral.exporter.exporter import Exporter


class ClipboardExporter(Exporter):
    def __init__(self):
        super().__init__("Clipboard")

    def export(self, name: str, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        if wavelengths is None:
            dat = spectra.T
            fmt = ["%.18e"] * spectra.shape[0]
        else:
            dat = np.column_stack((wavelengths.T, spectra.T))
            fmt = ["%g"] + ["%.18e"] * spectra.shape[0]

        output = io.StringIO()
        np.savetxt(output, dat, delimiter="\t", fmt=fmt)

        clipboard = QApplication.clipboard()
        clipboard.setText(output.getvalue())
