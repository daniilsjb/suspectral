from unittest.mock import MagicMock

import numpy as np
import pytest

from suspectral.exporter.exporter import Exporter
from suspectral.exporter.formatter import Formatter
from suspectral.exporter.writer import Writer


@pytest.fixture
def mock_formatter():
    mock_formatter = MagicMock(spec=Formatter)
    mock_formatter.format.return_value = "Lorem ipsum dolor sit amet, consectetuer"
    return mock_formatter

@pytest.fixture
def mock_writer():
    return MagicMock(spec=Writer)


@pytest.fixture
def victim(mock_formatter, mock_writer):
    return Exporter(
        label="Exporter",
        writer=mock_writer,
        formatter=mock_formatter,
    )

def test_exporter_with_wavelengths(victim, mock_formatter, mock_writer):
    spectra = np.random.rand(5, 3)
    wavelengths = np.linspace(400, 700, 5)

    name = "test_export"
    victim.export(name, spectra, wavelengths)

    mock_formatter.format.assert_called_once_with(spectra, wavelengths)
    mock_writer.write.assert_called_once_with(name, "Lorem ipsum dolor sit amet, consectetuer")


def test_exporter_without_wavelengths(victim, mock_formatter, mock_writer):
    spectra = np.random.rand(4, 2)
    name = "no-wavelengths"

    victim = Exporter("Binary Exporter", writer=mock_writer, formatter=mock_formatter)
    victim.export(name, spectra)

    mock_formatter.format.assert_called_once_with(spectra, None)
    mock_writer.write.assert_called_once_with(name, "Lorem ipsum dolor sit amet, consectetuer")
