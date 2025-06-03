from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import pytestqt
from PySide6.QtCore import QPoint, QEvent
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QApplication

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.spectral.spectral_view import SpectralView


@pytest.fixture
def mock_model():
    mock = MagicMock()
    mock.hypercube.name = "test_cube"
    return mock


@pytest.fixture
def victim(qtbot, mock_model):
    widget = SpectralView(model=mock_model)
    qtbot.addWidget(widget)
    return widget


def test_set_wavelengths_with_units(victim):
    wavelengths = np.linspace(400, 700, 10)
    victim.set_wavelengths(wavelengths, unit="nm")
    assert np.array_equal(victim.wavelengths, wavelengths)
    assert victim.getViewBox().viewRange()[0][0] <= 400
    assert victim.getViewBox().viewRange()[0][1] >= 700
    assert victim.getAxis("bottom").label.toPlainText().strip() == "Wavelength (nm)"


def test_set_wavelengths_without_units(victim):
    wavelengths = np.linspace(400, 700, 10)
    victim.set_wavelengths(wavelengths)
    assert victim.wavelengths is wavelengths
    assert victim.getViewBox().viewRange()[0][0] <= 400
    assert victim.getViewBox().viewRange()[0][1] >= 700
    assert victim.getAxis("bottom").label.toPlainText().strip() == "Wavelength"


def test_set_band_numbers(victim):
    victim.set_band_numbers(50)
    assert victim.wavelengths is None
    assert victim.getViewBox().viewRange()[0][0] <= 0
    assert victim.getViewBox().viewRange()[0][1] >= 50
    assert victim.getAxis("bottom").label.toPlainText().strip() == "Band Number"


def test_add_spectrum(victim):
    spectrum = np.ones(10)
    victim.add_spectrum(spectrum)
    assert np.array_equal(victim.spectra[0], spectrum)
    assert len(victim.listDataItems()) == 1


def test_clear_spectra(victim):
    victim._spectra.append(np.ones(10))
    victim.clear_spectra()

    assert len(victim.spectra) == 0
    assert len(victim.listDataItems()) == 0


def test_reset(victim):
    victim._spectra = [np.array([1, 2, 3])]
    victim._wavelengths = np.array([1, 2, 3])

    victim.reset()

    assert victim.wavelengths is None
    assert victim.spectra.size == 0

    assert victim.getViewBox().viewRange()[0][0] <= 0
    assert victim.getViewBox().viewRange()[0][1] >= 1

    assert victim.getAxis("bottom").label.toPlainText().strip() == "Wavelength"


def test_context_menu_signal_emitted_with_spectra(qtbot, victim):
    victim.add_spectrum(np.ones(10))
    event = QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse,
        QPoint(10, 10),
        victim.mapToGlobal(QPoint(10, 10)),
    )

    with qtbot.waitSignal(victim.contextMenuRequested, timeout=500):
        victim.contextMenuEvent(event)


def test_context_menu_signal_not_emitted_without_spectra(qtbot, victim):
    event = QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse,
        QPoint(10, 10),
        victim.mapToGlobal(QPoint(10, 10)),
    )

    with pytest.raises(pytestqt.exceptions.TimeoutError):
        with qtbot.waitSignal(victim.contextMenuRequested, timeout=300):
            victim.contextMenuEvent(event)
