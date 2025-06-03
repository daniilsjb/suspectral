import numpy as np
from PySide6.QtCore import Qt, Slot, Signal, QPoint
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
from suspectral.view.image.coloring_mode_rgb import ColoringModeRGB
from suspectral.view.image.coloring_mode_srf import ColoringModeSRF


class ImageControlsView(QStackedWidget):
    """
    A widget providing multiple image coloring mode controls for visualizing hypercube data.

    Signals
    -------
    imagedChanged(np.ndarray)
        Emitted when a new RGB image should be rendered.

    Parameters
    ----------
    model : HypercubeContainer
        The data model containing the hyperspectral hypercube used by the coloring modes.
    parent : QWidget or None, optional
        The parent QWidget of this widget, by default None.
    """

    imagedChanged = Signal(np.ndarray)

    def __init__(self,
                 model: HypercubeContainer,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Base)

        self._placeholder = QLabel("Load a hypercube to view image image.", self)
        self._placeholder.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._placeholder.setContentsMargins(4, 4, 4, 4)

        self._active: bool = False
        self._modes: list[ColoringMode] = []
        self._mode_dropdown = QComboBox(self)
        self._mode_controls = QStackedWidget(self)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:", self))
        mode_layout.addWidget(self._mode_dropdown)
        mode_layout.setSpacing(16)

        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        controls_layout.setSpacing(8)
        controls_layout.addLayout(mode_layout)
        controls_layout.addWidget(separator)
        controls_layout.addWidget(self._mode_controls)

        self._controls = QWidget(self)
        self._controls.setLayout(controls_layout)

        self.addWidget(self._placeholder)
        self.addWidget(self._controls)

        self._band_coloring_rgb = ColoringModeRGB(model, self)
        self._band_coloring_rgb.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("Band Coloring (RGB)", self._band_coloring_rgb)

        self._band_coloring_grayscale = ColoringModeGrayscale(model, self)
        self._band_coloring_grayscale.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("Band Coloring (Grayscale)", self._band_coloring_grayscale)

        self._true_coloring_cie = ColoringModeCIE(model, self)
        self._true_coloring_cie.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("True Coloring (CIE)", self._true_coloring_cie)

        self._true_coloring_srf = ColoringModeSRF(model, self)
        self._true_coloring_srf.imageChanged.connect(self.imagedChanged.emit)
        self._add_mode("True Coloring (SRF)", self._true_coloring_srf)

        self._mode_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._mode_dropdown.currentIndexChanged.connect(self._handle_mode_changed)

    def clear_reference_points(self):
        """Clear all spectral reference points from coloring modes that support them."""
        self._true_coloring_srf.clear_reference_points()
        self._true_coloring_cie.clear_reference_points()

    def add_reference_points(self, point: QPoint):
        """
        Add a new spectral reference point to coloring modes that support them.

        Parameters
        ----------
        point : QPoint
            The image coordinate to use as a reference point.
        """
        self._true_coloring_srf.add_reference_point(point)
        self._true_coloring_cie.add_reference_point(point)

    @Slot()
    def activate(self):
        """Activates the currently selected coloring mode."""
        self._active = True
        self._mode_dropdown.blockSignals(True)
        self._mode_dropdown.setCurrentIndex(0)
        self._mode_dropdown.blockSignals(False)
        self._handle_mode_changed(0)
        self.setCurrentWidget(self._controls)

    @Slot()
    def deactivate(self):
        """Deactivates all coloring modes."""
        self._active = False
        self.setCurrentWidget(self._placeholder)
        for mode in self._modes:
            mode.deactivate()

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
            self._modes[index].activate()
