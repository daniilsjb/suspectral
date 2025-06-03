import io

import numpy as np
import pytest

from suspectral.exporter.formatter_numpy import NpyFormatter


@pytest.fixture
def victim():
    return NpyFormatter()


def test_npy_format_with_wavelengths(victim):
    wavelengths = np.array([400, 500, 600])
    spectra = np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ])

    serialized = victim.format(spectra, wavelengths)
    assert isinstance(serialized, bytes)

    loaded = np.load(io.BytesIO(serialized))
    assert np.array_equal(loaded, np.vstack((wavelengths, spectra)))


def test_npy_format_without_wavelengths(victim):
    spectra = np.array([
        [1.0, 2.0],
        [3.0, 4.0],
    ])

    serialized = victim.format(spectra)
    assert isinstance(serialized, bytes)

    loaded = np.load(io.BytesIO(serialized))
    assert np.array_equal(loaded, spectra)
