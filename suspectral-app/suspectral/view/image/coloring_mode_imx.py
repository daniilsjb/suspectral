from io import BytesIO
from typing import cast

import numpy as np
from PySide6.QtCore import Signal, QThread, Slot, QObject, QResource
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressDialog, QPushButton, QSizePolicy
from scipy import integrate
from scipy import interpolate

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.coloring_mode import ColoringMode


class ColoringModeIMX(ColoringMode):
    def __init__(self, model: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._model = model
        self._model.opened.connect(self._handle_hypercube_opened)

        button = QPushButton("Generate")
        button.clicked.connect(self._handle_synthesis)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setToolTip("Starts the image synthesis process.")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("There are no configurable options for this image."))
        layout.addWidget(button)
        layout.setSpacing(8)

        self.setLayout(layout)

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        self.statusChanged.emit(hypercube.wavelengths is not None)

    @Slot()
    def _handle_synthesis(self):
        self._progress_dialog = QProgressDialog(self)
        self._progress_dialog.setWindowTitle("Generating...")
        self._progress_dialog.setLabelText(
            "Please, wait while the image is being synthesized. This may take a while...")
        self._progress_dialog.setModal(True)
        self._progress_dialog.show()

        self._thread = QThread()
        self._worker = SynthesizerIMX(self._model.hypercube)

        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._thread.deleteLater)

        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._progress_dialog.setValue)
        self._worker.finished.connect(self._progress_dialog.close)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(self._thread.quit)
        self._worker.produced.connect(self.imageChanged.emit)

        self._progress_dialog.canceled.connect(self._handle_cancel)
        self._thread.start()

    @Slot()
    def _handle_cancel(self):
        if self._worker:
            self._worker.stop()


class SynthesizerIMX(QObject):
    progress = Signal(int)
    finished = Signal()
    produced = Signal(np.ndarray)

    def __init__(self, hypercube: Hypercube):
        super().__init__()

        resource = QResource("/data/Sony_IMX219.csv")
        with BytesIO(cast(bytes, resource.data())) as file:
          imx219 = np.loadtxt(file, delimiter=",", skiprows=1)

        self._srf_w = imx219[:, 0]
        self._srf_r = imx219[:, 1]
        self._srf_g = imx219[:, 2]
        self._srf_b = imx219[:, 3]
        self._hypercube = hypercube
        self._running = True

    @Slot()
    def run(self):
        wavelengths = self._hypercube.wavelengths

        srf_w_min = max(wavelengths.min(), self._srf_w.min())
        srf_w_max = min(wavelengths.max(), self._srf_w.max())
        srf_w_mask = (wavelengths >= srf_w_min) & (wavelengths <= srf_w_max)
        wavelengths = wavelengths[srf_w_mask]

        srf_r = interpolate.CubicSpline(self._srf_w, self._srf_r)(wavelengths)
        srf_g = interpolate.CubicSpline(self._srf_w, self._srf_g)(wavelengths)
        srf_b = interpolate.CubicSpline(self._srf_w, self._srf_b)(wavelengths)

        srf_r /= integrate.simpson(srf_r, wavelengths)
        srf_g /= integrate.simpson(srf_g, wavelengths)
        srf_b /= integrate.simpson(srf_b, wavelengths)

        image = np.zeros((self._hypercube.num_rows, self._hypercube.num_cols, 3))

        for row in range(self._hypercube.num_rows):
            if not self._running: break

            spectra = self._hypercube.read_subregion((row, row + 1), (0, self._hypercube.num_cols))
            spectra = spectra[:, :, srf_w_mask]

            image[row, :, 0] = integrate.simpson(spectra * srf_r, wavelengths)
            image[row, :, 1] = integrate.simpson(spectra * srf_g, wavelengths)
            image[row, :, 2] = integrate.simpson(spectra * srf_b, wavelengths)

            self.progress.emit(int(row / (self._hypercube.num_rows - 1) * 100))
        else:
            image -= image.min(axis=(0, 1), keepdims=True)
            image /= image.max(axis=(0, 1), keepdims=True)
            self.produced.emit(image)

        self.finished.emit()

    def stop(self):
        self._running = False
