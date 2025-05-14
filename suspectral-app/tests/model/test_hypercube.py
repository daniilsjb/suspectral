import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from suspectral.model.hypercube import Hypercube


@pytest.fixture
def victim():
    mock = MagicMock()
    mock.metadata = {
        "default bands": ["2", "1", "0"],
        "wavelength unit": "nm"
    }
    mock.nrows = 100
    mock.ncols = 200
    mock.nbands = 10
    mock.sample_size = 2
    mock.shape = (100, 200, 10)
    mock.bands.centers = list(range(10, 110, 10))
    mock.read_pixel.return_value = np.array([1, 2, 3])
    mock.read_subregion.return_value = np.ones((10, 10, 3))
    mock.read_subimage.return_value = np.ones((10, 10, 3))
    return mock


@patch("suspectral.model.hypercube.envi.open")
def test_init_properties(mock_open, victim):
    mock_open.return_value = victim
    cube = Hypercube("dummy/path/ipsum.hdr")

    assert cube.name == "ipsum"
    assert cube.metadata == victim.metadata
    assert cube.num_rows == 100
    assert cube.num_cols == 200
    assert cube.num_bands == 10
    assert cube.bytes_per_sample == 2
    assert cube.num_samples == 100 * 200 * 10
    assert cube.num_bytes == 100 * 200 * 10 * 2
    assert cube.shape == (100, 200, 10)
    assert cube.wavelengths_unit == "nm"
    assert cube.default_bands == (2, 1, 0)
    np.testing.assert_array_equal(cube.wavelengths, np.array(sorted(victim.bands.centers)))


@patch("suspectral.model.hypercube.envi.open")
def test_wavelengths_fallback(mock_open):
    victim = MagicMock()
    victim.bands.centers = None

    mock_open.return_value = victim
    cube = Hypercube("dummy/path/file.hdr")
    assert cube.wavelengths is None


@patch("suspectral.model.hypercube.envi.open")
def test_default_bands_fallback(mock_open, victim):
    del victim.metadata["default bands"]
    mock_open.return_value = victim
    cube = Hypercube("dummy/path/file.hdr")

    assert cube.default_bands == (9, 5, 0)


@patch("suspectral.model.hypercube.envi.open")
@patch("suspectral.model.hypercube.get_rgb")
def test_get_rgb(mock_get_rgb, mock_open, victim):
    mock_open.return_value = victim
    mock_get_rgb.return_value = np.ones((10, 10, 3))
    cube = Hypercube("dummy/path/file.hdr")

    rgb = cube.get_rgb(1, 2, 3)
    mock_get_rgb.assert_called_once_with(victim, (1, 2, 3))
    np.testing.assert_array_equal(rgb, np.ones((10, 10, 3)))


@patch("suspectral.model.hypercube.envi.open")
@patch("suspectral.model.hypercube.get_rgb")
def test_get_grayscale(mock_get_rgb, mock_open, victim):
    mock_open.return_value = victim
    mock_get_rgb.return_value = np.ones((10, 10, 3))
    cube = Hypercube("dummy/path/file.hdr")

    gray = cube.get_grayscale(5)
    mock_get_rgb.assert_called_once_with(victim, (5, 5, 5))
    np.testing.assert_array_equal(gray, np.ones((10, 10, 3)))


@patch("suspectral.model.hypercube.envi.open")
def test_read_pixel(mock_open, victim):
    mock_open.return_value = victim
    cube = Hypercube("dummy/path/file.hdr")

    pixel = cube.read_pixel(10, 20)
    victim.read_pixel.assert_called_once_with(10, 20)
    np.testing.assert_array_equal(pixel, np.array([1, 2, 3]))


@patch("suspectral.model.hypercube.envi.open")
def test_read_pixels(mock_open, victim):
    mock_open.return_value = victim
    cube = Hypercube("dummy/path/file.hdr")

    result = cube.read_pixels([(0, 0), (1, 1)])
    assert victim.read_pixel.call_count == 2
    assert result.shape == (2, 3)


@patch("suspectral.model.hypercube.envi.open")
def test_read_subregion(mock_open, victim):
    mock_open.return_value = victim
    cube = Hypercube("dummy/path/file.hdr")

    result = cube.read_subregion((0, 10), (0, 10), bands=[1, 2, 3])
    victim.read_subregion.assert_called_once_with((0, 10), (0, 10), [1, 2, 3])
    assert result.shape == (10, 10, 3)


@patch("suspectral.model.hypercube.envi.open")
def test_read_subimage(mock_open, victim):
    mock_open.return_value = victim
    cube = Hypercube("dummy/path/file.hdr")

    result = cube.read_subimage((0, 10), (0, 10), bands=[1, 2, 3])
    victim.read_subimage.assert_called_once_with((0, 10), (0, 10), [1, 2, 3])
    assert result.shape == (10, 10, 3)
