import numpy as np
import pytest

from suspectral.exporter.formatter_csv import CsvFormatter


@pytest.fixture
def victim():
    return CsvFormatter()


def test_csv_format_without_wavelengths(victim):
    spectra = np.array([
        [0.1, 0.4],
        [0.2, 0.5],
        [0.3, 0.6],
    ])

    expected = (
        "1.000000000000000056e-01\t2.000000000000000111e-01\t2.999999999999999889e-01\n"
        "4.000000000000000222e-01\t5.000000000000000000e-01\t5.999999999999999778e-01\n"
    )

    result = victim.format(spectra)
    assert result == expected


def test_csv_format_with_wavelengths(victim):
    wavelengths = np.array([400, 500])
    spectra = np.array([
        [0.1, 0.4],
        [0.2, 0.5],
        [0.3, 0.6],
    ])

    expected = (
        "400\t1.000000000000000056e-01\t2.000000000000000111e-01\t2.999999999999999889e-01\n"
        "500\t4.000000000000000222e-01\t5.000000000000000000e-01\t5.999999999999999778e-01\n"
    )

    result = victim.format(spectra, wavelengths)
    assert result == expected
