import numpy as np
import pytest
from PySide6.QtCore import QObject, Signal

from suspectral.view.image.coloring_mode_grayscale import ColoringModeGrayscale


class DummyHypercube:
    def __init__(self, num_bands=5, wavelengths=None, default_bands=None, wavelengths_unit="nm"):
        self.num_bands = num_bands
        self.wavelengths = wavelengths
        self.default_bands = default_bands or [0]
        self.wavelengths_unit = wavelengths_unit

    def get_grayscale(self, band):
        return f"grayscale_band_{band}"


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
def grayscale_widget(hypercube_container, qtbot):
    widget = ColoringModeGrayscale(hypercube_container)
    qtbot.addWidget(widget)
    return widget


def test_initial_state(grayscale_widget):
    assert grayscale_widget._indexing == "Band Number"
    assert grayscale_widget._channel is not None


def test_handle_hypercube_opened_band_number(grayscale_widget, hypercube_container):
    hypercube = DummyHypercube(num_bands=10, wavelengths=None)
    hypercube_container.emit_opened(hypercube)

    assert grayscale_widget._num_bands == 10
    assert not grayscale_widget.indexing_dropdown.isVisible()
    assert grayscale_widget._band == 0


def test_handle_hypercube_opened_wavelength(qtbot, grayscale_widget, hypercube_container):
    wavelengths = np.array([400, 500, 600, 700])
    hypercube = DummyHypercube(num_bands=4, wavelengths=wavelengths)
    hypercube_container.emit_opened(hypercube)
    assert np.array_equal(grayscale_widget._wavelengths, wavelengths)


def test_set_indexing_switches_modes(grayscale_widget, hypercube_container):
    wavelengths = np.array([400, 500, 600])
    hypercube = DummyHypercube(num_bands=3, wavelengths=wavelengths)
    hypercube_container.emit_opened(hypercube)

    grayscale_widget._set_indexing("Wavelength")
    assert grayscale_widget._indexing == "Wavelength"

    grayscale_widget._set_indexing("Band Number")
    assert grayscale_widget._indexing == "Band Number"


def test_on_band_changed_emits_image_changed_signal(qtbot, grayscale_widget, hypercube_container):
    wavelengths = np.array([100, 200, 300])
    hypercube = DummyHypercube(num_bands=3, wavelengths=wavelengths)
    hypercube_container.emit_opened(hypercube)

    with qtbot.waitSignal(grayscale_widget.imageChanged, timeout=1000) as blocker:
        grayscale_widget._on_band_changed(1)

    assert blocker.args == ["grayscale_band_1"]


def test_get_band_index_band_number(grayscale_widget):
    grayscale_widget._indexing = "Band Number"
    result = grayscale_widget._get_band_index(2)
    assert result == 2


def test_get_band_index_wavelength(grayscale_widget):
    grayscale_widget._indexing = "Wavelength"
    grayscale_widget._wavelengths = np.array([400, 500, 600])
    result = grayscale_widget._get_band_index(510)
    assert result == 1


def test_reset_band_number(grayscale_widget):
    grayscale_widget._indexing = "Band Number"
    grayscale_widget._num_bands = 10
    grayscale_widget._band = 3
    grayscale_widget._reset()

    assert grayscale_widget._channel.spinbox.value() == 3
    assert grayscale_widget._channel.slider.value() == 3
    assert grayscale_widget._channel.slider.minimum() == 0
    assert grayscale_widget._channel.slider.maximum() == 9


def test_reset_wavelength(grayscale_widget):
    grayscale_widget._indexing = "Wavelength"
    grayscale_widget._band = 1
    grayscale_widget._wavelengths = np.array([450, 550, 650])
    grayscale_widget._model.hypercube = DummyHypercube(wavelengths_unit="nm")
    grayscale_widget._reset()

    assert grayscale_widget._channel.spinbox.value() == 550
    assert grayscale_widget._channel.slider.value() == 550
    assert grayscale_widget._channel.slider.minimum() == 450
    assert grayscale_widget._channel.slider.maximum() == 650
    assert grayscale_widget._channel.spinbox.suffix() == "nm"

def test_grayscale_start_emits_image_changed(grayscale_widget, qtbot):
    grayscale_widget._band = 2
    grayscale_widget._model.hypercube = DummyHypercube()

    with qtbot.waitSignal(grayscale_widget.imageChanged, timeout=500) as blocker:
        grayscale_widget.start()

    assert blocker.args[0] == "grayscale_band_2"
