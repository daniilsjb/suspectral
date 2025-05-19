import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from suspectral.view.image.band_color_channel import BandColorChannel


@pytest.fixture
def victim(qtbot):
    widget = BandColorChannel("Test")
    qtbot.addWidget(widget)
    return widget


def test_initial_state_with_label(victim):
    layout = victim.layout()
    label = layout.itemAt(0).widget()
    assert isinstance(label, QLabel)
    assert label.text() == "Test"


def test_initial_state_without_label(qtbot):
    widget = BandColorChannel()
    qtbot.addWidget(widget)
    layout = widget.layout()
    assert layout.count() == 2
    assert not isinstance(layout.itemAt(0).widget(), QLabel)


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


def test_slider_update_updates_spinbox(victim):
    victim.reset(0, 100, 20)
    victim.slider.setValue(70)
    victim._on_slider_update()
    assert victim.spinbox.value() == 70


def test_spinbox_update_updates_slider_and_emits_signal(victim, qtbot):
    victim.reset(0, 100, 20)
    with qtbot.waitSignal(victim.valueChanged, timeout=500) as blocker:
        victim.spinbox.setValue(80)
    assert victim.slider.value() == 80
    assert blocker.args == [80]


def test_spinbox_change_triggers_signal(victim, qtbot):
    victim.reset(0, 100, 20)

    with qtbot.waitSignal(victim.valueChanged, timeout=500):
        victim.spinbox.setValue(30)
