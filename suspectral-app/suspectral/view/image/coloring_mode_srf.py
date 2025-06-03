from PySide6.QtCore import QThread, Slot, QPoint
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QProgressDialog,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.coloring_mode import ColoringMode
from suspectral.view.image.spectral_reference import SpectralReference
from suspectral.view.image.spectral_selector import SpectralSelector
from suspectral.view.image.synthesizer_srf import SynthesizerSRF


class ColoringModeSRF(ColoringMode):
    """
    A spectral response function (SRF)-based coloring mode for hyperspectral image rendering.

    This widget allows the user to simulate how a hyperspectral image would appear when captured
    by a specific sensor with known spectral response functions. Optionally, a spectral power
    distribution (SPD) of the scene illuminant and white/black reference points can be provided
    to enhance realism. Image synthesis is performed asynchronously to avoid blocking the UI.

    Signals
    -------
    imageChanged : Signal(np.ndarray)
        Emitted when a new RGB image is generated.
    statusChanged : Signal(bool)
        Indicates whether this mode is enabled for this hypercube.

    Parameters
    ----------
    model : HypercubeContainer
        The container providing access to the current hypercube.
    parent : QWidget or None, optional
        The parent QWidget of this widget, by default None.
    """

    def __init__(self, model: HypercubeContainer, parent: QWidget | None = None):
        super().__init__(parent)
        self._model = model
        self._model.opened.connect(self._handle_hypercube_opened)

        srf_columns = ["Wavelength", "R", "G", "B"]
        srf_presets = [
            ("Sony IMX219", "/data/sensitivities/SRF_SonyIMX219.csv"),
            ("Basler Ace 2", "/data/sensitivities/SRF_BaslerAce2.csv"),
        ]

        self._srf_field = SpectralSelector(columns=srf_columns, presets=srf_presets, parent=self)
        self._srf_field.setToolTip(
            "(Required) These spectra will be interpreted as the red (R), green (G), and blue (B)\n"
            "spectral response functions of the sensor, which describe its sensitivity to light."
        )

        srf_layout = QHBoxLayout()
        srf_layout.addWidget(QLabel("Sensor SRF:"), stretch=0)
        srf_layout.addWidget(self._srf_field, stretch=1)

        spd_columns = ["Wavelength", "Intensity"]
        spd_presets = [
            ("CIE A", "/data/illuminants/CIE_std_illum_A.csv"),
            ("CIE D50", "/data/illuminants/CIE_std_illum_D50.csv"),
            ("CIE D65", "/data/illuminants/CIE_std_illum_D65.csv"),
        ]

        self._spd_field = SpectralSelector(columns=spd_columns, presets=spd_presets, parent=self)
        self._spd_field.setToolTip(
            "If specified, this spectrum will be interpreted as the spectral power distribution\n"
            "of the scene illuminant, which may affect the colour temperature of the image."
        )

        spd_layout = QHBoxLayout()
        spd_layout.addWidget(QLabel("Illuminant:"), stretch=0)
        spd_layout.addWidget(self._spd_field, stretch=1)

        self._contrast_checkbox = QCheckBox(self)
        self._contrast_checkbox.setChecked(False)
        self._contrast_checkbox.setText("Apply per-channel contrast")
        self._contrast_checkbox.setToolTip(
            "If enabled, each color channel of the synthesized RGB image will be separately\n"
            "normalized by subtracting its minimum value and dividing by its maximum value.")

        self._points: list[QPoint] = []
        self._white_ref_select = SpectralReference(model, parent=self)
        self._white_ref_select.setToolTip(
            "If specified, the spectrum of this pixel will be used to approximate the spectral\n"
            "power distribution of the scene illuminant, making it the brightest in the image."
        )

        white_ref_layout = QHBoxLayout()
        white_ref_layout.addWidget(QLabel("White:"), stretch=0)
        white_ref_layout.addWidget(self._white_ref_select, stretch=1)

        self._black_ref_select = SpectralReference(model, parent=self)
        self._black_ref_select.setToolTip(
            "If specified, the spectrum of this pixel will be used to approximate the spectral\n"
            "bias of the imaging spectrometer device, making it the darkest in the image."
        )

        black_ref_layout = QHBoxLayout()
        black_ref_layout.addWidget(QLabel("Black:"), stretch=0)
        black_ref_layout.addWidget(self._black_ref_select, stretch=1)

        self._generate = QPushButton("Generate", parent=self)
        self._generate.clicked.connect(self._handle_synthesis)
        self._generate.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._generate.setToolTip("Starts the image synthesis process.")
        self._generate.setEnabled(False)

        self._srf_field.valueChanged.connect(lambda: self._generate.setEnabled(True))
        self._srf_field.valueCleared.connect(lambda: self._generate.setEnabled(False))

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(srf_layout)
        layout.addLayout(spd_layout)
        layout.addLayout(white_ref_layout)
        layout.addLayout(black_ref_layout)
        layout.addWidget(self._contrast_checkbox)
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self._generate)

    def deactivate(self):
        self.clear_reference_points()
        self._spd_field.clear()
        self._srf_field.clear()

    def clear_reference_points(self):
        """Clears any previously added white or black reference pixels."""
        self._white_ref_select.clear()
        self._black_ref_select.clear()

    def add_reference_point(self, point: QPoint):
        """
        Adds a pixel position as a candidate for both white and black reference spectra.

        Parameters
        ----------
        point : QPoint
            The image coordinate to consider as a reference.
        """
        self._white_ref_select.add(point)
        self._black_ref_select.add(point)

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        self.statusChanged.emit(hypercube.wavelengths is not None)

    @Slot()
    def _handle_synthesis(self):
        self._progress_dialog = QProgressDialog(self)
        self._progress_dialog.setWindowTitle("Generating...")
        self._progress_dialog.setModal(True)
        self._progress_dialog.setLabelText(
            "Please, wait while the image is being synthesized. This may take a while..."
        )

        self._worker = SynthesizerSRF(
            srf=self._srf_field.data_,
            spd=self._spd_field.data_,
            hypercube=self._model.hypercube,
            white_ref=self._white_ref_select.get(),
            black_ref=self._black_ref_select.get(),
            apply_per_channel_contrast=self._contrast_checkbox.isChecked(),
        )

        self._thread = QThread()
        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._thread.deleteLater)

        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._progress_dialog.setValue)
        self._worker.finished.connect(self._progress_dialog.close)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(self._thread.quit)
        self._worker.produced.connect(self.imageChanged.emit)

        self._progress_dialog.show()
        self._progress_dialog.canceled.connect(self._handle_cancel)
        self._thread.start()

    @Slot()
    def _handle_cancel(self):
        if self._worker:
            self._worker.stop()
