import io

import numpy as np
from PySide6.QtWidgets import QApplication

from suspectral.exporter.exporter import Exporter


class ClipboardExporter(Exporter):
    def __init__(self):
        super().__init__("Clipboard")

    def export(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        data = spectra.T
        fmt = ["%.18e"] * spectra.shape[0]

        if wavelengths is not None:
            data = np.column_stack((wavelengths.T, spectra.T))
            fmt.insert(0, "%g")

        output = io.StringIO()
        np.savetxt(output, data, delimiter="\t", fmt=fmt)

        clipboard = QApplication.clipboard()
        clipboard.setText(output.getvalue())
