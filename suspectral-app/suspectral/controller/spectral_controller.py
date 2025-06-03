import numpy as np
from PySide6.QtCore import QObject, Slot, QPoint, QStandardPaths
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QApplication, QFileDialog, QMessageBox

from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.manager import ToolManager
from suspectral.view.spectral.spectral_view import SpectralView
from suspectral.theme_icon import ThemeIcon


class SpectralController(QObject):
    """
    Controller which synchronizes interactions between the model and view.

    Parameters
    ----------
    view : SpectralView
        The view component responsible for displaying spectral plots.
    tools : ToolManager
        The tool manager handling user interaction tools.
    model : HypercubeContainer
        The model containing the current hypercube dataset.
    exporters : list of Exporter
        A list of available exporter plugins for exporting spectral data.
    parent : QObject or None, optional
        The parent object of the controller, by default None.
    """

    def __init__(self, *,
                 view: SpectralView,
                 tools: ToolManager,
                 model: HypercubeContainer,
                 exporters: list[Exporter],
                 parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._model = model
        self._exporters = exporters

        model.opened.connect(self._handle_hypercube_opened)
        model.closed.connect(self._handle_hypercube_closed)

        view.contextMenuRequested.connect(self._handle_context_menu)

        tools.toolChanged.connect(self._handle_tool_changed)

        tools.inspect.pixelClicked.connect(self._handle_pixel_clicked)
        tools.inspect.pixelCleared.connect(self._handle_pixel_cleared)

        tools.area.selectionMoved.connect(self._handle_selection_changed)
        tools.area.selectionEnded.connect(self._handle_selection_changed)
        tools.area.selectionSampled.connect(self._handle_selection_sampled)

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        if hypercube.wavelengths is None:
            self._view.set_band_numbers(hypercube.num_bands)
            return

        self._view.set_wavelengths(
            hypercube.wavelengths,
            hypercube.wavelengths_unit,
        )

    @Slot()
    def _handle_hypercube_closed(self):
        self._view.reset()

    @Slot()
    def _handle_tool_changed(self):
        self._view.clear_spectra()

    @Slot()
    def _handle_pixel_clicked(self, point: QPoint):
        spectrum = self._model.hypercube.read_pixel(point.y(), point.x())
        self._view.add_spectrum(spectrum)

    @Slot()
    def _handle_pixel_cleared(self):
        self._view.clear_spectra()

    @Slot()
    def _handle_selection_changed(self):
        self._view.clear_spectra()

    @Slot()
    def _handle_selection_sampled(self, xs: np.ndarray, ys: np.ndarray):
        spectra = self._model.hypercube.read_subimage(ys, xs)
        spectra = spectra.reshape(-1, spectra.shape[-1])
        for spectrum in spectra:
            self._view.add_spectrum(spectrum)

    @Slot()
    def _handle_context_menu(self, menu: QMenu):
        copy_action = QAction("Copy Image", self)
        copy_action.setIcon(ThemeIcon("copy.svg"))
        copy_action.triggered.connect(self._copy_plot)
        menu.addAction(copy_action)

        save_action = QAction("Save Image As...", self)
        save_action.setIcon(ThemeIcon("image.svg"))
        save_action.triggered.connect(self._save_plot)
        menu.addAction(save_action)

        menu.addSeparator()

        for exporter in self._exporters:
            action = QAction(f"Export to {exporter.label}", self)
            action.triggered.connect(lambda _, _exporter=exporter: self._export_spectra(_exporter))
            menu.addAction(action)

    def _copy_plot(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self._view.grab())

    def _save_plot(self):
        downloads = QStandardPaths \
            .writableLocation(QStandardPaths.StandardLocation.DownloadLocation)

        path, _ = QFileDialog.getSaveFileName(
            self._view,
            caption="Save Plot",
            filter="PNG (*.png);;JPG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;BMP (*.bmp)",
            dir=f"{downloads}/{self._model.hypercube.name}.png",
        )

        if not path: return
        if not self._view.grab().save(path):
            QMessageBox.critical(
                self._view,
                "Export Failed",
                "Couldn't export the image to the specified file path. Please, ensure that you've "
                "selected one of the supported image formats and that the target directory is accessible.",
            )

    def _export_spectra(self, exporter: Exporter):
        exporter.export(
            self._model.hypercube.name,
            self._view.spectra,
            self._view.wavelengths,
        )
