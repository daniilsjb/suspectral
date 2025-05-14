import numpy as np
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.band_color_channel import BandColorChannel
from suspectral.view.image.coloring_mode import ColoringMode


class ColoringModeGrayscale(ColoringMode):
    def __init__(self, model: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._model = model
        self._model.opened.connect(self._handle_hypercube_opened)

        self._indexing = "Band Number"
        self._wavelengths = np.array([])
        self._num_bands = None

        self._band = None
        self._channel = BandColorChannel()
        self._channel.valueChanged.connect(self._on_band_changed)

        channels_layout = QVBoxLayout()
        channels_layout.addWidget(self._channel)
        channels_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        channels_layout.setSpacing(8)

        self.indexing_label = QLabel("Indexing:")
        self.indexing_dropdown = QComboBox()
        self.indexing_dropdown.addItem("Band Number")
        self.indexing_dropdown.addItem("Wavelength")
        self.indexing_dropdown.currentTextChanged.connect(self._set_indexing)
        self.indexing_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        indexing_layout = QHBoxLayout()
        indexing_layout.addWidget(self.indexing_label)
        indexing_layout.addWidget(self.indexing_dropdown)
        indexing_layout.setSpacing(16)

        layout = QVBoxLayout()
        layout.addLayout(indexing_layout)
        layout.addLayout(channels_layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        self._num_bands = hypercube.num_bands
        self._wavelengths = hypercube.wavelengths

        indexing_enabled = hypercube.wavelengths is not None
        self.indexing_label.setVisible(indexing_enabled)
        self.indexing_dropdown.setVisible(indexing_enabled)

        if not indexing_enabled:
            self.indexing_dropdown.setCurrentText("Band Number")

        self._band = hypercube.default_bands[0]
        self._reset()

    def start(self):
        self._on_band_changed(self._band)

    def _set_indexing(self, value: str):
        self._indexing = value
        self._reset()

    def _on_band_changed(self, value: int):
        self._band = self._get_band_index(value)
        self.imageChanged.emit(self._model.hypercube.get_grayscale(self._band))

    def _get_band_index(self, value: int):
        if self._indexing == "Wavelength":
            return int(np.argmin(np.square(value - self._wavelengths)))
        else:
            return value

    def _reset(self):
        if self._indexing == "Wavelength":
            minimum = int(min(self._wavelengths))
            maximum = int(max(self._wavelengths))
            suffix = self._model.hypercube.wavelengths_unit or ""
            self._channel.reset(minimum, maximum, self._wavelengths[self._band], suffix)
        else:
            self._channel.reset(0, self._num_bands - 1, self._band)

