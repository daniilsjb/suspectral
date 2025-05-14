import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QSize, QStandardPaths, Slot
from PySide6.QtGui import QAction, QContextMenuEvent
from PySide6.QtWidgets import QFileDialog, QMenu, QWidget, QApplication

from suspectral.colors import get_color
from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer


class SpectralView(pg.PlotWidget):
    def __init__(self, model: HypercubeContainer, exporters: list[Exporter], parent: QWidget | None = None):
        super().__init__(parent)
        self._exporters = exporters
        self._model = model

        self._spectra: list[np.ndarray] = []
        self._wavelengths: np.ndarray | None = None

        self.getViewBox().setMenuEnabled(False)
        self.getViewBox().setMouseEnabled(x=False, y=False)
        self.getPlotItem().setContentsMargins(10, 20, 20, 10)

        self.setLabel("left", "Intensity")
        self.setLabel("bottom", "Wavelength")

    def sizeHint(self) -> QSize:
        return QSize(400, 200)

    @Slot()
    def set_wavelengths(self, wavelengths: np.ndarray, unit: str | None = None):
        self._wavelengths = wavelengths
        self.setXRange(wavelengths.min(), wavelengths.max())
        self.setLabel("bottom", f"Wavelength ({unit})" if unit else "Wavelength", unit=unit)

    @Slot()
    def set_bands(self, num_bands: int):
        self._wavelengths = None
        self.setXRange(0, num_bands)
        self.setLabel("bottom", f"Band Number")

    @Slot()
    def add_spectrum(self, spectrum: np.ndarray):
        pen = pg.mkPen(get_color(len(self._spectra)))
        if self._wavelengths is not None:
            self.plot(self._wavelengths, spectrum, pen=pen, antialias=True)
        else:
            self.plot(spectrum, pen=pen, antialias=True)

        self._spectra.append(spectrum)

    @Slot()
    def clear_spectra(self):
        self.clear()
        self._spectra.clear()

    @Slot()
    def reset(self):
        self.clear_spectra()
        self.setYRange(0, 1)
        self.setXRange(0, 1)
        self.getPlotItem().enableAutoRange(True, True)
        self.setLabel("bottom", "Wavelength")
        self._wavelengths = None

    def contextMenuEvent(self, event: QContextMenuEvent):
        if not self._spectra: return

        menu = QMenu(self)
        self._add_save_actions(menu)
        menu.addSeparator()
        self._add_export_actions(menu)
        menu.exec(event.globalPos())

    def _add_save_actions(self, menu: QMenu):
        copy_action = QAction("Copy Image", self)
        copy_action.triggered.connect(self._copy_plot)
        menu.addAction(copy_action)

        save_action = QAction("Save Image As...", self)
        save_action.triggered.connect(self._save_plot)
        menu.addAction(save_action)

    def _copy_plot(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.grab())

    def _save_plot(self):
        downloads = QStandardPaths \
            .writableLocation(QStandardPaths.StandardLocation.DownloadLocation)

        name = self._model.hypercube.name
        path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save Plot",
            filter="PNG (*.png);;JPG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;BMP (*.bmp)",
            dir=f"{downloads}/{name}.png",
        )

        if path:
            self.grab().save(path)

    def _add_export_actions(self, menu: QMenu):
        for exporter in self._exporters:
            action = QAction(f"Export to {exporter.label}", self)
            action.triggered.connect(lambda _, it=exporter: self._export_spectra(it))
            menu.addAction(action)

    def _export_spectra(self, exporter: Exporter):
        hypercube = self._model.hypercube
        exporter.export(hypercube.name, np.array(self._spectra), self._wavelengths)
