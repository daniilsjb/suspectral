import numpy as np
import pytest
from PySide6.QtCore import QPoint

from suspectral.controller.spectral_controller import SpectralController


@pytest.fixture
def mock_view(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_tools(mocker):
    inspect = mocker.Mock()
    area = mocker.Mock()
    tool_manager = mocker.Mock(inspect=inspect, area=area)
    return tool_manager


@pytest.fixture
def mock_model(mocker):
    model = mocker.Mock()
    model.hypercube = mocker.Mock()
    return model


@pytest.fixture
def victim(qtbot, mock_view, mock_tools, mock_model):
    return SpectralController(view=mock_view, tools=mock_tools, model=mock_model)


def test_handle_hypercube_opened_with_wavelengths(victim, mock_view, mocker):
    mock_cube = mocker.Mock()
    mock_cube.wavelengths = [1, 2, 3]
    mock_cube.wavelengths_unit = "nm"

    victim._handle_hypercube_opened(mock_cube)

    mock_view.set_wavelengths.assert_called_once_with([1, 2, 3], "nm")
    mock_view.set_bands.assert_not_called()


def test_handle_hypercube_opened_without_wavelengths(victim, mock_view, mocker):
    mock_cube = mocker.Mock()
    mock_cube.wavelengths = None
    mock_cube.num_bands = 42

    victim._handle_hypercube_opened(mock_cube)

    mock_view.set_bands.assert_called_once_with(42)
    mock_view.set_wavelengths.assert_not_called()


def test_handle_hypercube_closed(victim, mock_view):
    victim._handle_hypercube_closed()
    mock_view.reset.assert_called_once()


def test_handle_tool_changed(victim, mock_view):
    victim._handle_tool_changed()
    mock_view.clear_spectra.assert_called_once()


def test_handle_pixel_clicked(victim, mock_view, mock_model):
    spectrum = np.array([0.1, 0.2, 0.3])
    mock_model.hypercube.read_pixel.return_value = spectrum

    victim._handle_pixel_clicked(QPoint(5, 10))

    mock_model.hypercube.read_pixel.assert_called_once_with(10, 5)
    mock_view.add_spectrum.assert_called_once_with(spectrum)


def test_handle_pixel_cleared(victim, mock_view):
    victim._handle_pixel_cleared()
    mock_view.clear_spectra.assert_called_once()


def test_handle_selection_changed(victim, mock_view):
    victim._handle_selection_changed()
    mock_view.clear_spectra.assert_called_once()


def test_handle_selection_sampled(victim, mock_view, mock_model):
    xs = np.array([0, 1])
    ys = np.array([1, 2])
    spectra = np.array([
        [[0.1, 0.2], [0.3, 0.4]],
        [[0.5, 0.6], [0.7, 0.8]]
    ])  # shape (2, 2, 2)

    mock_model.hypercube.read_subimage.return_value = spectra

    victim._handle_selection_sampled(xs, ys)

    expected_spectra = spectra.reshape(-1, 2)
    calls = [((spectrum,),) for spectrum in expected_spectra]

    actual_calls = mock_view.add_spectrum.call_args_list
    assert len(actual_calls) == len(expected_spectra)

    for call, expected in zip(actual_calls, calls):
        assert np.allclose(call.args[0], expected[0])
