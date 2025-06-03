import numpy as np
import pytest
import io
from scipy.io import loadmat

from suspectral.exporter.formatter_matlab import MatlabFormatter


@pytest.fixture
def victim():
    return MatlabFormatter()


def test_matlab_format_with_wavelengths(victim):
    wavelengths = np.array([400, 500])
    spectra = np.array([
        [0.1, 0.4],
        [0.2, 0.5],
        [0.3, 0.6],
    ])

    serialized = victim.format(spectra, wavelengths)
    assert isinstance(serialized, bytes)

    loaded = loadmat(io.BytesIO(serialized))
    assert np.array_equal(loaded["spectra"], spectra)
    assert np.array_equal(loaded["wavelengths"].squeeze(), wavelengths)

def test_matlab_format_without_wavelengths(victim):
    spectra = np.array([
        [1.0, 2.0],
        [3.0, 4.0],
    ])

    serialized = victim.format(spectra)
    assert isinstance(serialized, bytes)

    loaded = loadmat(io.BytesIO(serialized))
    assert np.array_equal(loaded["spectra"], spectra)
    assert "wavelengths" not in loaded
