from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QApplication, QMenu

from suspectral.view.spectral_view import SpectralView


@pytest.fixture
def mock_model():
    mock = MagicMock()
    mock.hypercube.name = "test_cube"
    return mock


@pytest.fixture
def mock_exporter():
    exporter = MagicMock()
    exporter.label = "MockFormat"
    return exporter


@pytest.fixture
def victim(qtbot, mock_model, mock_exporter):
    widget = SpectralView(model=mock_model, exporters=[mock_exporter])
    qtbot.addWidget(widget)
    return widget


def test_size_hint(victim):
    hint = victim.sizeHint()
    assert hint.width() == 400
    assert hint.height() == 200


def test_set_wavelengths(victim):
    wavelengths = np.linspace(400, 700, 10)
    victim.set_wavelengths(wavelengths, unit="nm")
    assert victim._wavelengths is wavelengths
    x_range = victim.getViewBox().viewRange()[0]
    assert x_range[0] <= 400
    assert x_range[1] >= 700


def test_set_bands(victim):
    victim.set_bands(50)
    assert victim._wavelengths is None
    x_range = victim.getViewBox().viewRange()[0]
    assert x_range[0] <= 0
    assert x_range[1] >= 50


@patch("suspectral.view.spectral_view.get_color", return_value='r')
def test_add_spectrum_without_wavelengths(mock_color, victim):
    spectrum = np.random.rand(10)
    victim.set_bands(10)
    victim.add_spectrum(spectrum)
    assert spectrum in victim._spectra
    assert len(victim.listDataItems()) == 1


@patch("suspectral.view.spectral_view.get_color", return_value='g')
def test_add_spectrum_with_wavelengths(mock_color, victim):
    wavelengths = np.linspace(400, 700, 10)
    spectrum = np.random.rand(10)
    victim.set_wavelengths(wavelengths)
    victim.add_spectrum(spectrum)
    assert spectrum in victim._spectra
    assert len(victim.listDataItems()) == 1


def test_clear_spectra(victim):
    spectrum = np.random.rand(10)
    victim._spectra.append(spectrum)
    victim.plot(np.arange(10), spectrum)
    assert len(victim._spectra) == 1
    assert len(victim.listDataItems()) == 1
    victim.clear_spectra()
    assert len(victim._spectra) == 0
    assert len(victim.listDataItems()) == 0


def test_reset(victim):
    victim._spectra = [np.array([1, 2, 3])]
    victim._wavelengths = np.array([1, 2, 3])
    victim.reset()
    assert victim._wavelengths is None
    assert victim._spectra == []

    x_range = victim.getViewBox().viewRange()[0]
    assert x_range[0] <= 0
    assert x_range[1] >= 1


def test_context_menu_with_spectra(victim):
    victim._spectra.append(np.random.rand(10))

    with patch("suspectral.view.spectral_view.QMenu") as MockMenu:
        mock_menu_instance = MagicMock()
        MockMenu.return_value = mock_menu_instance

        event = QContextMenuEvent(
            QContextMenuEvent.Reason.Mouse,
            victim.rect().center(),
            victim.mapToGlobal(victim.rect().center())
        )

        victim.contextMenuEvent(event)

        MockMenu.assert_called_once_with(victim)
        assert mock_menu_instance.exec.called


def test_copy_plot(victim):
    with patch.object(QApplication, "clipboard") as mock_clipboard:
        clipboard_instance = MagicMock()
        mock_clipboard.return_value = clipboard_instance
        victim._copy_plot()
        clipboard_instance.setPixmap.assert_called_once()


def test_save_plot(victim, mock_model):
    with patch("suspectral.view.spectral_view.QFileDialog.getSaveFileName", return_value=("test.png", "PNG")), \
            patch.object(victim, "grab", return_value=MagicMock()) as mock_grab:
        pixmap = mock_grab.return_value
        victim._save_plot()
        pixmap.save.assert_called_with("test.png")


def test_save_plot_cancel(victim):
    with patch("suspectral.view.spectral_view.QFileDialog.getSaveFileName", return_value=("", "")), \
            patch.object(victim, "grab", return_value=MagicMock()) as mock_grab:
        victim._save_plot()
        mock_grab.return_value.save.assert_not_called()


def test_add_export_actions(victim, mock_exporter):
    menu = QMenu()
    victim._add_export_actions(menu)
    actions = menu.actions()
    assert len(actions) == 1
    assert actions[0].text() == "Export to MockFormat"


def test_export_spectra(victim, mock_exporter, mock_model):
    spectrum = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    victim._spectra = [spectrum]
    victim._wavelengths = np.arange(400, 700, 10)
    victim._export_spectra(mock_exporter)

    args = mock_exporter.export.call_args[0]
    assert args[0] == "test_cube"
    assert np.array_equal(args[1], np.array([spectrum]))
    assert np.array_equal(args[2], victim._wavelengths)
