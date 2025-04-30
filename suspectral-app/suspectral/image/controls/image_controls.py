import numpy as np
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPalette, QImage
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from suspectral.hypercube.hypercube import Hypercube
from suspectral.hypercube.hypercube_container import HypercubeContainer
from suspectral.image.controls.band_coloring_grayscale import BandColoringGrayscale
from suspectral.image.controls.band_coloring_rgb import BandColoringRGB
from suspectral.image.controls.coloring_mode import ColoringMode
from suspectral.image.controls.true_coloring_cie import TrueColoringCIE
from suspectral.image.controls.true_coloring_imx import TrueColoringIMX


class ImageControls(QStackedWidget):
    image_changed = Signal(QImage)

    def __init__(self, container: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._container = container
        self._container.opened.connect(self.handle_hypercube_opened)

        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Base)

        self._placeholder = QLabel("Load a hypercube to view image controls.")
        self._placeholder.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._placeholder.setContentsMargins(4, 4, 4, 4)

        self._modes: dict[str, ColoringMode] = {}
        self._mode_controls = QStackedWidget()
        self._mode_name: str | None = None

        self._mode_dropdown = QComboBox()
        self._mode_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        mode_layout.addWidget(self._mode_dropdown)
        mode_layout.setSpacing(16)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        controls_layout.setSpacing(8)
        controls_layout.addLayout(mode_layout)
        controls_layout.addWidget(separator)
        controls_layout.addWidget(self._mode_controls)

        self._controls = QWidget()
        self._controls.setLayout(controls_layout)

        self.addWidget(self._placeholder)
        self.addWidget(self._controls)

        band_coloring_rgb_controls = BandColoringRGB(container)
        band_coloring_rgb_controls.image_changed.connect(self._handle_image_changed)
        self._add_mode("Band Coloring (RGB)", band_coloring_rgb_controls)

        band_coloring_grayscale_controls = BandColoringGrayscale(container)
        band_coloring_grayscale_controls.image_changed.connect(self._handle_image_changed)
        self._add_mode("Band Coloring (Grayscale)", band_coloring_grayscale_controls)

        true_coloring_cie_controls = TrueColoringCIE(container)
        true_coloring_cie_controls.image_changed.connect(self._handle_image_changed)
        self._add_mode("True Coloring (CIE 1931)", true_coloring_cie_controls)

        true_coloring_imx_controls = TrueColoringIMX(container)
        true_coloring_imx_controls.image_changed.connect(self._handle_image_changed)
        self._add_mode("True Coloring (Sony IMX219)", true_coloring_imx_controls)

        self._mode_dropdown.currentTextChanged.connect(self._handle_mode_changed)

    def open(self):
        if self._container.hypercube.wavelengths is None:
            self._mode_dropdown.setCurrentText("Band Coloring (RGB)")

        for mode in self._modes.values():
            mode.reset()

        self.setCurrentWidget(self._controls)
        self._modes[self._mode_name].activate()

    def close(self):
        self.setCurrentWidget(self._placeholder)

    def _add_mode(self, name: str, mode: ColoringMode):
        self._modes[name] = mode
        self._mode_dropdown.addItem(name)
        self._mode_controls.addWidget(mode)
        if self._mode_name is None:
            self._mode_name = name

    @Slot()
    def _handle_mode_changed(self, name: str):
        self._mode_name = name
        self._mode_controls.setCurrentWidget(self._modes[name])
        if self._container.hypercube:
            self._modes[name].activate()

    @Slot()
    def _handle_image_changed(self, data: np.ndarray):
        height, width, channels = data.shape
        image_bytes = np.ascontiguousarray((data * 255).astype(np.uint8)).tobytes()
        image = QImage(image_bytes, width, height, channels * width, QImage.Format.Format_RGB888)
        self.image_changed.emit(image)

    @Slot()
    def handle_hypercube_opened(self, hypercube: Hypercube):
        enabled = hypercube.wavelengths is not None
        self._mode_dropdown.model().item(2).setEnabled(enabled)
        self._mode_dropdown.model().item(3).setEnabled(enabled)
