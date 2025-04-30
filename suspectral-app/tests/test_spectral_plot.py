from unittest.mock import MagicMock

import numpy as np
import pytest

from suspectral.spectral.spectral_plot_view import SpectralPlotView


@pytest.fixture
def victim(qtbot):
    exporter_csv = MagicMock()
    exporter_csv.name = "CSV"

    exporter_npy = MagicMock()
    exporter_npy.name = "NPy"

    plot = SpectralPlotView(exporters=[exporter_csv, exporter_npy])
    qtbot.addWidget(plot)

    return plot


def test_set_wavelengths_with_unit(victim):
    wavelengths = np.array([400, 500, 600])
    victim.set_wavelengths(wavelengths, unit="nm")
    assert victim.getAxis("bottom").label.toPlainText().strip() == "Wavelength (nm)"


def test_set_wavelengths_without_unit(victim):
    wavelengths = np.array([400, 500, 600])
    victim.set_wavelengths(wavelengths)
    assert victim.getAxis("bottom").label.toPlainText().strip() == "Wavelength"


def test_add_spectrum(victim):
    victim.set_wavelengths(np.array([400, 500, 600]))
    victim.add_spectrum(np.array([1.0, 2.0, 3.0]))
    assert len(victim._spectra) == 1


def test_clear_spectra(victim):
    victim.set_wavelengths(np.array([400, 500, 600]))
    victim.add_spectrum(np.array([1.0, 2.0, 3.0]))
    victim.clear_spectra()

    assert len(victim._spectra) == 0


def test_reset(victim):
    victim.set_wavelengths(np.array([400, 500, 600]))
    victim.add_spectrum(np.array([1.0, 2.0, 3.0]))
    victim.reset()

    assert victim._wavelengths is None
    assert len(victim._spectra) == 0
    assert victim.getAxis("bottom").label.toPlainText().strip() == "Wavelength"


def test_export_spectra(victim):
    wavelengths = np.array([400, 500, 600])
    spectrum_1 = np.array([1.0, 2.0, 3.0])
    spectrum_2 = np.array([4.0, 5.0, 6.0])

    victim.set_wavelengths(wavelengths)
    victim.add_spectrum(spectrum_1)
    victim.add_spectrum(spectrum_2)

    exporter = victim._exporters[0]
    victim._export_spectra(exporter)
    exporter.export.assert_called_once()

    exported_spectra = exporter.export.call_args[0][0]
    assert np.array_equal(exported_spectra[0], spectrum_1)
    assert np.array_equal(exported_spectra[1], spectrum_2)

    exported_wavelengths = exporter.export.call_args[0][1]
    assert np.array_equal(exported_wavelengths, wavelengths)
