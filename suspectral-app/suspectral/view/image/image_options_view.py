import numpy as np
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QPalette
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

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.coloring_mode import ColoringMode
from suspectral.view.image.coloring_mode_cie import ColoringModeCIE
from suspectral.view.image.coloring_mode_grayscale import ColoringModeGrayscale
from suspectral.view.image.coloring_mode_imx import ColoringModeIMX
from suspectral.view.image.coloring_mode_rgb import ColoringModeRGB


class ImageOptionsView(QStackedWidget):
    imagedChanged = Signal(np.ndarray)

    def __init__(self,
                 model: HypercubeContainer,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Base)

        self._placeholder = QLabel("Load a hypercube to view image image.")
        self._placeholder.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._placeholder.setContentsMargins(4, 4, 4, 4)

        self._active: bool = False
        self._modes: list[ColoringMode] = []
        self._mode_dropdown = QComboBox()
        self._mode_controls = QStackedWidget()

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

        band_coloring_rgb = ColoringModeRGB(model, self)
        band_coloring_rgb.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("Band Coloring (RGB)", band_coloring_rgb)

        band_coloring_grayscale = ColoringModeGrayscale(model, self)
        band_coloring_grayscale.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("Band Coloring (Grayscale)", band_coloring_grayscale)

        true_coloring_cie = ColoringModeCIE(model)
        true_coloring_cie.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("True Coloring (CIE 1931)", true_coloring_cie)

        true_coloring_imx = ColoringModeIMX(model)
        true_coloring_imx.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("True Coloring (Sony IMX219)", true_coloring_imx)

        self._mode_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._mode_dropdown.currentIndexChanged.connect(self._handle_mode_changed)

    @Slot()
    def activate(self):
        self._active = True
        self._mode_dropdown.blockSignals(True)
        self._mode_dropdown.setCurrentIndex(0)
        self._mode_dropdown.blockSignals(False)
        self._handle_mode_changed(0)
        self.setCurrentWidget(self._controls)

    @Slot()
    def deactivate(self):
        self._active = False
        self.setCurrentWidget(self._placeholder)

    def _add_mode(self, name: str, mode: ColoringMode):
        self._modes.append(mode)
        self._mode_dropdown.addItem(name)
        self._mode_controls.addWidget(mode)

        index = len(self._modes) - 1
        mode.statusChanged.connect(
            lambda enabled: self._mode_dropdown.model() \
                .item(index).setEnabled(enabled)
        )

    @Slot()
    def _handle_mode_changed(self, index: int):
        self._mode_controls.setCurrentWidget(self._modes[index])
        if self._active:
            self._modes[index].start()
