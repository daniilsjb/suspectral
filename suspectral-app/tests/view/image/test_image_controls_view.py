from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QWidget

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.image_controls_view import ImageControlsView


class DummyColoringMode(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)

        self.activate = MagicMock()
        self.deactivate = MagicMock()

        self.imageChanged = MagicMock()
        self.statusChanged = MagicMock()

        self.add_reference_point = MagicMock()
        self.clear_reference_points = MagicMock()


@pytest.fixture
def mock_model():
    return MagicMock(spec=HypercubeContainer)


@pytest.fixture
def victim(qtbot, mock_model):
    with patch("suspectral.view.image.image_controls_view.ColoringModeRGB", new=DummyColoringMode), \
            patch("suspectral.view.image.image_controls_view.ColoringModeCIE", new=DummyColoringMode), \
            patch("suspectral.view.image.image_controls_view.ColoringModeSRF", new=DummyColoringMode), \
            patch("suspectral.view.image.image_controls_view.ColoringModeGrayscale", new=DummyColoringMode):
        victim = ImageControlsView(mock_model)
        qtbot.addWidget(victim)
        return victim


def test_initial_state(victim):
    assert not victim._active
    assert victim.currentWidget() == victim._placeholder
    assert victim._mode_dropdown.count() == 4


def test_activate_sets_controls_view(victim):
    victim.activate()
    assert victim._active
    assert victim.currentWidget() == victim._controls
    assert victim._mode_controls.currentWidget() == victim._modes[0]


def test_deactivate_resets_modes(victim):
    for mode in victim._modes:
        mode.deactivate = MagicMock()

    victim.activate()
    victim.deactivate()

    assert not victim._active
    assert victim.currentWidget() == victim._placeholder
    for mode in victim._modes:
        mode.deactivate.assert_called_once()


def test_clear_reference_points(victim):
    victim._true_coloring_srf.clear_reference_points = MagicMock()
    victim._true_coloring_cie.clear_reference_points = MagicMock()

    victim.clear_reference_points()

    victim._true_coloring_srf.clear_reference_points.assert_called_once()
    victim._true_coloring_cie.clear_reference_points.assert_called_once()


def test_add_reference_points(victim):
    victim._true_coloring_srf.add_reference_point = MagicMock()
    victim._true_coloring_cie.add_reference_point = MagicMock()

    point = QPoint(10, 15)
    victim.add_reference_points(point)

    victim._true_coloring_srf.add_reference_point.assert_called_once_with(point)
    victim._true_coloring_cie.add_reference_point.assert_called_once_with(point)


def test_mode_change_switches_widget(victim):
    victim.activate()
    assert victim._mode_controls.currentWidget() == victim._modes[0]

    victim._handle_mode_changed(2)
    assert victim._mode_controls.currentWidget() == victim._modes[2]
