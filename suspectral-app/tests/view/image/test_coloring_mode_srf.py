from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PySide6.QtCore import QPoint

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.coloring_mode_srf import ColoringModeSRF


@pytest.fixture
def mock_model():
    model = MagicMock(spec=HypercubeContainer)
    model.hypercube = MagicMock()
    return model


@pytest.fixture
def victim(qtbot, mock_model):
    victim = ColoringModeSRF(model=mock_model)
    qtbot.addWidget(victim)
    return victim


def test_initialization(victim):
    assert not victim._contrast_checkbox.isChecked()


def test_clear_reference_points(victim):
    victim._white_ref_select.clear = MagicMock()
    victim._black_ref_select.clear = MagicMock()

    victim.clear_reference_points()

    victim._white_ref_select.clear.assert_called_once()
    victim._black_ref_select.clear.assert_called_once()


def test_add_reference_point(victim):
    victim._white_ref_select.add = MagicMock()
    victim._black_ref_select.add = MagicMock()

    point = QPoint(5, 5)
    victim.add_reference_point(point)

    victim._white_ref_select.add.assert_called_once_with(point)
    victim._black_ref_select.add.assert_called_once_with(point)


def test_deactivate(victim):
    victim.clear_reference_points = MagicMock()
    victim._srf_field.clear = MagicMock()
    victim._spd_field.clear = MagicMock()

    victim.deactivate()

    victim.clear_reference_points.assert_called_once()
    victim._srf_field.clear.assert_called_once()
    victim._spd_field.clear.assert_called_once()


def test_handle_hypercube_opened_emits_status(qtbot, victim):
    victim.statusChanged = MagicMock()

    hypercube = MagicMock()
    hypercube.wavelengths = np.linspace(400, 700, 100)

    victim._handle_hypercube_opened(hypercube)
    victim.statusChanged.emit.assert_called_once_with(True)


def test_handle_hypercube_opened_emits_false_on_none(qtbot, victim):
    victim.statusChanged = MagicMock()

    hypercube = MagicMock()
    hypercube.wavelengths = None

    victim._handle_hypercube_opened(hypercube)
    victim.statusChanged.emit.assert_called_once_with(False)


@patch("suspectral.view.image.coloring_mode_srf.SynthesizerSRF")
@patch("suspectral.view.image.coloring_mode_srf.QProgressDialog")
def test_handle_synthesis_starts_thread(mock_dialog_cls, mock_synth_cls, victim, qtbot):
    mock_worker = MagicMock()
    mock_synth_cls.return_value = mock_worker

    mock_dialog = MagicMock()
    mock_dialog_cls.return_value = mock_dialog

    victim._srf_field.data_ = np.array([4.0, 5.0, 6.0])
    victim._spd_field.data_ = np.array([1.0, 2.0, 3.0])
    victim._white_ref_select.get = MagicMock(return_value=np.array([0.1, 0.2, 0.3]))
    victim._black_ref_select.get = MagicMock(return_value=np.array([0.0, 0.0, 0.1]))
    victim._contrast_checkbox.setChecked(True)

    victim._handle_synthesis()

    mock_synth_cls.assert_called_once()
    args, kwargs = mock_synth_cls.call_args

    assert np.array_equal(kwargs["srf"], victim._srf_field.data_)
    assert np.array_equal(kwargs["spd"], victim._spd_field.data_)
    assert kwargs["apply_per_channel_contrast"] is True

    mock_dialog_cls.assert_called_once()
    mock_worker.moveToThread.assert_called_once()
    mock_dialog.show.assert_called_once()


@patch("suspectral.view.image.coloring_mode_srf.SynthesizerSRF")
@patch("suspectral.view.image.coloring_mode_srf.QProgressDialog")
def test_handle_cancel_stops_worker(_mock_dialog_cls, _mock_synth_cls, victim):
    mock_worker = MagicMock()
    victim._worker = mock_worker
    victim._handle_cancel()
    mock_worker.stop.assert_called_once()
