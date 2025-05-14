from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from suspectral.exporter.exporter_clipboard import ClipboardExporter


@pytest.fixture
def spectra():
    return np.array([[1.0, 2.0], [3.0, 4.0]])


@pytest.fixture
def wavelengths():
    return np.array([100.0, 200.0])


@patch("suspectral.exporter.exporter_clipboard.QApplication.clipboard")
def test_export_without_wavelengths(mock_clipboard, spectra):
    mock_clip = MagicMock()
    mock_clipboard.return_value = mock_clip

    victim = ClipboardExporter()
    victim.export(name="foo", spectra=spectra)

    expected_text = (
        "1.000000000000000000e+00\t3.000000000000000000e+00\n"
        "2.000000000000000000e+00\t4.000000000000000000e+00\n"
    )

    mock_clip.setText.assert_called_once_with(expected_text)


@patch("suspectral.exporter.exporter_clipboard.QApplication.clipboard")
def test_export_with_wavelengths(mock_clipboard, spectra, wavelengths):
    mock_clip = MagicMock()
    mock_clipboard.return_value = mock_clip

    victim = ClipboardExporter()
    victim.export(name="foo", spectra=spectra, wavelengths=wavelengths)

    expected_text = (
        "100\t1.000000000000000000e+00\t3.000000000000000000e+00\n"
        "200\t2.000000000000000000e+00\t4.000000000000000000e+00\n"
    )

    mock_clip.setText.assert_called_once_with(expected_text)
