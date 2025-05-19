import numpy as np
import pytest
from PySide6.QtCore import QObject, Signal

from suspectral.view.image.coloring_mode_rgb import ColoringModeRGB


class DummyHypercube:
    def __init__(self, num_bands=5, wavelengths=None, default_bands=None, wavelengths_unit="nm"):
        self.num_bands = num_bands
        self.wavelengths = wavelengths
        self.default_bands = default_bands or [0, 1, 2]
        self.wavelengths_unit = wavelengths_unit

    def get_rgb(self, r, g, b):
        return f"rgb_{r}_{g}_{b}"


class DummyHypercubeContainer(QObject):
    opened = Signal(object)

    def __init__(self):
        super().__init__()
        self.hypercube = None

    def emit_opened(self, hypercube):
        self.hypercube = hypercube
        self.opened.emit(hypercube)


@pytest.fixture
def hypercube_container():
    return DummyHypercubeContainer()


@pytest.fixture
def victim(hypercube_container, qtbot):
    widget = ColoringModeRGB(hypercube_container)
    qtbot.addWidget(widget)
    return widget


def test_reset_band_number(victim):
    victim._indexing = "Band Number"
    victim._num_bands = 10
    victim._band_r = 2
    victim._band_g = 5
    victim._band_b = 7
    victim._reset()

    assert victim._channel_r.spinbox.value() == 2
    assert victim._channel_g.spinbox.value() == 5
    assert victim._channel_b.spinbox.value() == 7


def test_reset_wavelength(victim):
    victim._indexing = "Wavelength"
    victim._wavelengths = np.array([450, 550, 650])
    victim._band_r = 0
    victim._band_g = 1
    victim._band_b = 2
    victim._model.hypercube = DummyHypercube(wavelengths_unit="nm")
    victim._reset()

    assert victim._channel_r.spinbox.value() == 450
    assert victim._channel_g.spinbox.value() == 550
    assert victim._channel_b.spinbox.value() == 650
    assert victim._channel_r.spinbox.suffix() == "nm"


def test_handle_hypercube_opened_wavelength(victim, hypercube_container, qtbot):
    wavelengths = np.array([400, 500, 600])
    hypercube = DummyHypercube(num_bands=3, wavelengths=wavelengths)
    hypercube_container.emit_opened(hypercube)

    assert np.array_equal(victim._wavelengths, wavelengths)
    assert victim._band_r == 0
    assert victim._band_g == 1
    assert victim._band_b == 2


def test_on_band_changed_emits_image_changed(victim, qtbot):
    victim._indexing = "Band Number"
    victim._num_bands = 5
    victim._band_r = 0
    victim._band_g = 1
    victim._band_b = 2
    victim._model.hypercube = DummyHypercube()

    with qtbot.waitSignal(victim.imageChanged, timeout=500) as blocker:
        victim._on_r_changed(3)

    assert blocker.args[0] == "rgb_3_1_2"


def test_start_emits_initial_rgb(victim, qtbot):
    victim._indexing = "Band Number"
    victim._band_r = 1
    victim._band_g = 2
    victim._band_b = 3
    victim._model.hypercube = DummyHypercube()

    with qtbot.waitSignal(victim.imageChanged, timeout=500) as blocker:
        victim.start()

    assert blocker.args[0] == "rgb_1_2_3"

def test_handle_hypercube_opened_without_wavelength(victim, hypercube_container, qtbot):
    hypercube = DummyHypercube(num_bands=3, wavelengths=None)
    hypercube_container.emit_opened(hypercube)
    assert victim.indexing_dropdown.currentText() == "Band Number"

def test_set_indexing_triggers_reset(victim, mocker):
    mock_reset = mocker.patch.object(victim, "_reset")

    victim._set_indexing("Wavelength")

    assert victim._indexing == "Wavelength"
    mock_reset.assert_called_once()

def test_on_g_changed_emits_correct_rgb(victim, qtbot):
    victim._indexing = "Band Number"
    victim._band_r = 1
    victim._band_g = 2
    victim._band_b = 3
    victim._model.hypercube = DummyHypercube()

    with qtbot.waitSignal(victim.imageChanged) as blocker:
        victim._on_g_changed(4)

    assert blocker.args[0] == "rgb_1_4_3"

def test_on_b_changed_emits_correct_rgb(victim, qtbot):
    victim._indexing = "Band Number"
    victim._band_r = 1
    victim._band_g = 2
    victim._band_b = 3
    victim._model.hypercube = DummyHypercube()

    with qtbot.waitSignal(victim.imageChanged) as blocker:
        victim._on_b_changed(0)

    assert blocker.args[0] == "rgb_1_2_0"

def test_get_band_index_wavelength_mode(victim):
    victim._indexing = "Wavelength"
    victim._wavelengths = np.array([450, 550, 650])

    index = victim._get_band_index(570)
    assert index == 1
