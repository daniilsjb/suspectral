import numpy as np
from PySide6.QtCore import Signal, Qt, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from suspectral.hypercube.hypercube import Hypercube
from suspectral.hypercube.hypercube_container import HypercubeContainer
from suspectral.image.controls.coloring_mode import ColoringMode


class BandColoringRGB(ColoringMode):
    def __init__(self, container: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._container = container
        self._container.opened.connect(self._handle_hypercube_opened)

        self._indexing = "Band Number"
        self._wavelengths = np.array([])
        self._num_bands = None

        self._band_r = None
        self._band_g = None
        self._band_b = None

        self._channel_r = BandColorChannel(name="R")
        self._channel_g = BandColorChannel(name="G")
        self._channel_b = BandColorChannel(name="B")

        self._channel_r.value_changed.connect(self._on_r_changed)
        self._channel_g.value_changed.connect(self._on_g_changed)
        self._channel_b.value_changed.connect(self._on_b_changed)

        channels_layout = QVBoxLayout()
        channels_layout.addWidget(self._channel_r)
        channels_layout.addWidget(self._channel_g)
        channels_layout.addWidget(self._channel_b)
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

    def reset(self):
        hypercube = self._container.hypercube

        self._num_bands = hypercube.num_bands
        self._wavelengths = hypercube.wavelengths

        if self._wavelengths is None:
            self.indexing_dropdown.setCurrentText("Band Number")

        r, g, b = hypercube.default_bands
        self._band_r = r
        self._band_g = g
        self._band_b = b
        self._reset()

    def activate(self):
        self._on_bands_changed(
            self._band_r,
            self._band_g,
            self._band_b,
        )

    def _reset(self):
        if self._indexing == "Wavelength":
            minimum = int(min(self._wavelengths))
            maximum = int(max(self._wavelengths))

            suffix = self._container.hypercube.wavelengths_unit or ""
            self._channel_r.reset(minimum, maximum, self._wavelengths[self._band_r], suffix)
            self._channel_g.reset(minimum, maximum, self._wavelengths[self._band_g], suffix)
            self._channel_b.reset(minimum, maximum, self._wavelengths[self._band_b], suffix)
        else:
            self._channel_r.reset(0, self._num_bands - 1, self._band_r)
            self._channel_g.reset(0, self._num_bands - 1, self._band_g)
            self._channel_b.reset(0, self._num_bands - 1, self._band_b)

    def _set_indexing(self, value: str):
        self._indexing = value
        self._reset()

    def _on_r_changed(self, value: int):
        self._band_r = self._get_band_index(value)
        self._on_bands_changed(self._band_r, self._band_g, self._band_b)

    def _on_g_changed(self, value: int):
        self._band_g = self._get_band_index(value)
        self._on_bands_changed(self._band_r, self._band_g, self._band_b)

    def _on_b_changed(self, value: int):
        self._band_b = self._get_band_index(value)
        self._on_bands_changed(self._band_r, self._band_g, self._band_b)

    def _on_bands_changed(self, r: int, g: int, b: int):
        self.image_changed.emit(self._container.hypercube.get_rgb(r, g, b))

    def _get_band_index(self, value: int):
        if self._indexing == "Wavelength":
            return int(np.argmin(np.square(value - self._wavelengths)))
        else:
            return value

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        indexing_enabled = hypercube.wavelengths is not None
        self.indexing_label.setVisible(indexing_enabled)
        self.indexing_dropdown.setVisible(indexing_enabled)


class BandColorChannel(QWidget):
    value_changed = Signal(int)

    def __init__(self, name: str):
        super().__init__()

        self.spinbox = QSpinBox()
        self.spinbox.valueChanged.connect(self._on_spinbox_update)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderReleased.connect(self._on_slider_update)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        layout = QHBoxLayout()
        layout.addWidget(QLabel(name))
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)

        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def reset(self, minimum: int, maximum: int, value: int, suffix: str = ""):
        self.slider.blockSignals(True)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.slider.setTickInterval((maximum - minimum) // 10)
        self.slider.blockSignals(False)

        self.spinbox.blockSignals(True)
        self.spinbox.setRange(minimum, maximum)
        self.spinbox.setValue(value)
        self.spinbox.setSuffix(suffix)
        self.spinbox.blockSignals(False)

    def _on_slider_update(self):
        value = self.slider.value()
        self.spinbox.setValue(value)

    def _on_spinbox_update(self, value: int):
        self.slider.setValue(value)
        self.value_changed.emit(value)
