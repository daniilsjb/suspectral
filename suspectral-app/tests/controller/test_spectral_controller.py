from unittest.mock import MagicMock

import numpy as np
import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QMenu

import resources
from suspectral.controller.spectral_controller import SpectralController
from suspectral.exporter.exporter import Exporter

assert resources


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
    exporter_a = MagicMock(spec=Exporter)
    exporter_b = MagicMock(spec=Exporter)
    exporter_c = MagicMock(spec=Exporter)

    exporter_a.label = "A"
    exporter_b.label = "B"
    exporter_c.label = "C"

    return SpectralController(
        view=mock_view,
        tools=mock_tools,
        model=mock_model,
        exporters=[
            exporter_a,
            exporter_b,
            exporter_c,
        ],
    )


def test_handle_hypercube_opened_with_wavelengths(victim, mock_view, mocker):
    mock_cube = mocker.Mock()
    mock_cube.wavelengths = [1, 2, 3]
    mock_cube.wavelengths_unit = "nm"

    victim._handle_hypercube_opened(mock_cube)

    mock_view.set_wavelengths.assert_called_once_with([1, 2, 3], "nm")
    mock_view.set_band_numbers.assert_not_called()


def test_handle_hypercube_opened_without_wavelengths(victim, mock_view, mocker):
    mock_cube = mocker.Mock()
    mock_cube.wavelengths = None
    mock_cube.num_bands = 42

    victim._handle_hypercube_opened(mock_cube)

    mock_view.set_band_numbers.assert_called_once_with(42)
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
    ])

    mock_model.hypercube.read_subimage.return_value = spectra

    victim._handle_selection_sampled(xs, ys)

    expected_spectra = spectra.reshape(-1, 2)
    calls = [((spectrum,),) for spectrum in expected_spectra]

    actual_calls = mock_view.add_spectrum.call_args_list
    assert len(actual_calls) == len(expected_spectra)

    for call, expected in zip(actual_calls, calls):
        assert np.allclose(call.args[0], expected[0])


def test_menu_content(victim, qtbot):
    menu = QMenu()
    victim._handle_context_menu(menu)

    labels = [action.text() for action in menu.actions() if not action.isSeparator()]
    assert labels == ["Copy Image", "Save Image As..."] + [
        f"Export to {exporter.label}" for exporter in victim._exporters
    ]


def test_copy_plot_calls_clipboard_with_grabbed_pixmap(victim, mocker):
    pixmap_mock = mocker.Mock()
    victim._view.grab.return_value = pixmap_mock

    clipboard_mock = mocker.Mock()
    mocker.patch("suspectral.controller.spectral_controller.QApplication.clipboard", return_value=clipboard_mock)

    victim._copy_plot()
    clipboard_mock.setPixmap.assert_called_once_with(pixmap_mock)


def test_save_plot_success(victim, mocker):
    pixmap_mock = mocker.Mock()
    pixmap_mock.save.return_value = True
    victim._view.grab.return_value = pixmap_mock
    victim._model.hypercube.name = "test_cube"

    mocker.patch("suspectral.controller.spectral_controller.QStandardPaths.writableLocation", return_value="/downloads")
    mocker.patch("suspectral.controller.spectral_controller.QFileDialog.getSaveFileName",
                 return_value=("/downloads/test.png", None))

    critical_mock = mocker.patch("suspectral.controller.spectral_controller.QMessageBox.critical")
    victim._save_plot()
    pixmap_mock.save.assert_called_once_with("/downloads/test.png")
    critical_mock.assert_not_called()


def test_save_plot_cancelled(victim, mocker):
    pixmap_mock = mocker.Mock()
    victim._view.grab.return_value = pixmap_mock

    mocker.patch("suspectral.controller.spectral_controller.QStandardPaths.writableLocation", return_value="/downloads")
    mocker.patch("suspectral.controller.spectral_controller.QFileDialog.getSaveFileName", return_value=("", None))

    victim._save_plot()
    pixmap_mock.save.assert_not_called()


def test_save_plot_failure_shows_critical(victim, mocker):
    pixmap_mock = mocker.Mock()
    pixmap_mock.save.return_value = False
    victim._view.grab.return_value = pixmap_mock
    victim._model.hypercube.name = "test_cube"

    mocker.patch("suspectral.controller.spectral_controller.QStandardPaths.writableLocation", return_value="/downloads")
    mocker.patch("suspectral.controller.spectral_controller.QFileDialog.getSaveFileName",
                 return_value=("/downloads/test.png", None))

    critical_mock = mocker.patch("suspectral.controller.spectral_controller.QMessageBox.critical")
    victim._save_plot()
    critical_mock.assert_called_once()
