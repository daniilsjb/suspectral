from io import BytesIO
from typing import cast

import numpy as np
from PySide6.QtCore import Signal, Slot, QObject, QThread, QResource
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QProgressDialog, QPushButton, QSizePolicy
from scipy import interpolate, integrate

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.coloring_mode import ColoringMode


class ColoringModeCIE(ColoringMode):
    def __init__(self, model: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._model = model
        self._model.opened.connect(self._handle_hypercube_opened)

        self._srgb_checkbox = QCheckBox()
        self._srgb_checkbox.setText("Apply sRGB conversion")
        self._srgb_checkbox.setChecked(False)

        self._gamma_checkbox = QCheckBox()
        self._gamma_checkbox.setText("Apply gamma correction")
        self._gamma_checkbox.setChecked(False)

        button = QPushButton("Generate")
        button.clicked.connect(self._handle_synthesis)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setToolTip("Starts the image synthesis process.")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._srgb_checkbox)
        layout.addWidget(self._gamma_checkbox)
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
        self._worker = SynthesizerCIE(
            hypercube=self._model.hypercube,
            apply_srgb=self._srgb_checkbox.isChecked(),
            apply_gamma=self._gamma_checkbox.isChecked(),
        )

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


class SynthesizerCIE(QObject):
    progress = Signal(int)
    finished = Signal()
    produced = Signal(np.ndarray)

    def __init__(self, hypercube: Hypercube, apply_srgb: bool = False, apply_gamma: bool = False):
        super().__init__()

        resource = QResource("/data/CIE_XYZ_1931.csv")
        with BytesIO(cast(bytes, resource.data())) as file:
          cmf = np.loadtxt(file, delimiter=",", skiprows=1)

        self._cmf_w = cmf[:, 0]
        self._cmf_x = cmf[:, 1]
        self._cmf_y = cmf[:, 2]
        self._cmf_z = cmf[:, 3]

        self._hypercube = hypercube
        self._apply_srgb = apply_srgb
        self._apply_gamma = apply_gamma

        self._running = True

    @Slot()
    def run(self):
        wavelengths = self._hypercube.wavelengths

        cmf_w_min = max(wavelengths.min(), self._cmf_w.min())
        cmf_w_max = min(wavelengths.max(), self._cmf_w.max())
        cmf_w_mask = (wavelengths >= cmf_w_min) & (wavelengths <= cmf_w_max)
        wavelengths = wavelengths[cmf_w_mask]

        cmf_x = interpolate.CubicSpline(self._cmf_w, self._cmf_x)(wavelengths)
        cmf_y = interpolate.CubicSpline(self._cmf_w, self._cmf_y)(wavelengths)
        cmf_z = interpolate.CubicSpline(self._cmf_w, self._cmf_z)(wavelengths)

        cmf_x /= integrate.simpson(cmf_x, wavelengths)
        cmf_y /= integrate.simpson(cmf_y, wavelengths)
        cmf_z /= integrate.simpson(cmf_z, wavelengths)

        image = np.zeros((self._hypercube.num_rows, self._hypercube.num_cols, 3))

        for row in range(self._hypercube.num_rows):
            if not self._running: break

            spectra = self._hypercube.read_subregion((row, row + 1), (0, self._hypercube.num_cols))
            spectra = spectra[:, :, cmf_w_mask]

            image[row, :, 0] = integrate.simpson(spectra * cmf_x, wavelengths)
            image[row, :, 1] = integrate.simpson(spectra * cmf_y, wavelengths)
            image[row, :, 2] = integrate.simpson(spectra * cmf_z, wavelengths)

            self.progress.emit(int(row / (self._hypercube.num_rows - 1) * 100))
        else:
            if self._apply_srgb:
                image = image.reshape(-1, 3).T
                image = np.array([
                    [+3.2404542, -1.5371385, -0.4985314],
                    [-0.9692660, +1.8760108, +0.0415560],
                    [+0.0556434, -0.2040259, +1.0572252],
                ]) @ image
                image = image.T.reshape((self._hypercube.num_rows, self._hypercube.num_cols, 3))

            image -= image.min(axis=(0, 1), keepdims=True)
            image /= image.max(axis=(0, 1), keepdims=True)

            if self._apply_gamma:
                gamma_map = image <= 0.0031308
                image[ gamma_map] = 12.92 * image[ gamma_map]
                image[~gamma_map] = 1.055 * image[~gamma_map] ** 0.416 - 0.055

            self.produced.emit(image)

        self.finished.emit()

    def stop(self):
        self._running = False
