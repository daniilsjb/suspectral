import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSpinBox, QSlider

from suspectral.view.image.band_color_channel import BandColorChannel


@pytest.fixture
def victim(qtbot):
    widget = BandColorChannel("Test")
    qtbot.addWidget(widget)
    return widget


def test_initial_state_with_label(victim):
    layout = victim.layout()
    assert layout.count() == 3
    assert isinstance(layout.itemAt(0).widget(), QLabel)
    assert isinstance(layout.itemAt(1).widget(), QSlider)
    assert isinstance(layout.itemAt(2).widget(), QSpinBox)
    assert layout.itemAt(0).widget().text() == "Test"


def test_initial_state_without_label(qtbot):
    victim = BandColorChannel()
    qtbot.addWidget(victim)

    layout = victim.layout()
    assert layout.count() == 2
    assert isinstance(layout.itemAt(0).widget(), QSlider)
    assert isinstance(layout.itemAt(1).widget(), QSpinBox)


def test_reset_sets_spinbox_and_slider(victim):
    victim.reset(0, 100, 50, "nm")
    assert victim.spinbox.minimum() == 0
    assert victim.spinbox.maximum() == 100
    assert victim.spinbox.value() == 50
    assert victim.spinbox.suffix() == "nm"

    assert victim.slider.minimum() == 0
    assert victim.slider.maximum() == 100
    assert victim.slider.value() == 50
    assert victim.slider.tickInterval() == 10


def test_slider_update_updates_spinbox(victim, qtbot):
    victim.reset(0, 100, 20)
    victim.slider.setValue(30)
    victim._on_slider_update()

    assert victim.slider.value() == 30
    assert victim.spinbox.value() == 30


def test_spinbox_update_updates_slider(victim):
    victim.reset(0, 100, 20)
    victim.spinbox.setValue(80)
    assert victim.slider.value() == 80


def test_spinbox_change_triggers_signal(victim, qtbot):
    victim.reset(0, 100, 20)

    with qtbot.waitSignal(victim.valueChanged, timeout=500):
        victim.spinbox.setValue(30)
