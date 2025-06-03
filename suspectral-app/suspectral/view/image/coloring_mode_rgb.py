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


class ColoringModeRGB(ColoringMode):
    """
    An RGB coloring mode for rendering hyperspectral data using three spectral bands.

    This widget provides controls to assign individual spectral bands to the red, green,
    and blue channels of an image. Users can select bands either by index or by wavelength.
    It automatically updates when a new hypercube is opened and emits RGB images based
    on user-selected band combinations.

    Signals
    -------
    imageChanged : Signal(np.ndarray)
        Emitted when a new RGB image should be rendered.

    Parameters
    ----------
    model : HypercubeContainer
        The container that manages and provides access to the currently loaded hypercube.
    parent : QWidget or None, optional
        The parent QWidget of this widget, by default None.
    """

    def __init__(self, model: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._model = model
        self._model.opened.connect(self._handle_hypercube_opened)

        self._indexing = "Band Number"
        self._wavelengths = np.array([])
        self._num_bands = None

        self._band_r = None
        self._band_g = None
        self._band_b = None

        self._channel_r = BandColorChannel(name="R", parent=self)
        self._channel_g = BandColorChannel(name="G", parent=self)
        self._channel_b = BandColorChannel(name="B", parent=self)

        self._channel_r.valueChanged.connect(self._on_r_changed)
        self._channel_g.valueChanged.connect(self._on_g_changed)
        self._channel_b.valueChanged.connect(self._on_b_changed)

        channels_layout = QVBoxLayout()
        channels_layout.addWidget(self._channel_r)
        channels_layout.addWidget(self._channel_g)
        channels_layout.addWidget(self._channel_b)
        channels_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        channels_layout.setSpacing(8)

        self._indexing_label = QLabel("Indexing:")
        self._indexing_dropdown = QComboBox(self)
        self._indexing_dropdown.addItem("Band Number")
        self._indexing_dropdown.addItem("Wavelength")
        self._indexing_dropdown.currentTextChanged.connect(self._set_indexing)
        self._indexing_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        indexing_layout = QHBoxLayout()
        indexing_layout.addWidget(self._indexing_label)
        indexing_layout.addWidget(self._indexing_dropdown)
        indexing_layout.setSpacing(16)

        layout = QVBoxLayout(self)
        layout.addLayout(indexing_layout)
        layout.addLayout(channels_layout)
        layout.setContentsMargins(0, 0, 0, 0)

    def activate(self):
        self._on_bands_changed(
            self._band_r,
            self._band_g,
            self._band_b,
        )

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        self._num_bands = hypercube.num_bands
        self._wavelengths = hypercube.wavelengths

        indexing_enabled = hypercube.wavelengths is not None
        self._indexing_label.setVisible(indexing_enabled)
        self._indexing_dropdown.setVisible(indexing_enabled)

        if not indexing_enabled:
            self._indexing_dropdown.setCurrentText("Band Number")

        r, g, b = hypercube.default_bands
        self._band_r = r
        self._band_g = g
        self._band_b = b
        self._reset()

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
        self.imageChanged.emit(self._model.hypercube.get_rgb(r, g, b))

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
            self._channel_r.reset(minimum, maximum, self._wavelengths[self._band_r], suffix)
            self._channel_g.reset(minimum, maximum, self._wavelengths[self._band_g], suffix)
            self._channel_b.reset(minimum, maximum, self._wavelengths[self._band_b], suffix)
        else:
            self._channel_r.reset(0, self._num_bands - 1, self._band_r)
            self._channel_g.reset(0, self._num_bands - 1, self._band_g)
            self._channel_b.reset(0, self._num_bands - 1, self._band_b)
