from pathlib import Path

import numpy as np
from spectral import get_rgb
from spectral.io import envi
from spectral.io.envi import (
    FileNotAnEnviHeader,
    EnviHeaderParsingError,
    MissingEnviHeaderParameter,
    EnviDataFileNotFoundError,
)


class Hypercube:
    """
    Represents a hyperspectral image stored in ENVI format.

    Provides access to image metadata, dimensions, wavelengths, and methods
    to read pixel spectra and extract RGB or grayscale images from the hyperspectral data.

    Parameters
    ----------
    path : str
        Path to the ENVI header file.

    Raises
    ------
    HypercubeDataMissing
        If the ENVI data file cannot be found.
    HypercubeHeaderInvalid
        If the ENVI header is invalid or missing required parameters.
    """

    def __init__(self, path: str):
        try:
            self._envi = envi.open(path)
            self._metadata = self._envi.metadata
        except EnviDataFileNotFoundError as e:
            raise HypercubeDataMissing(e)
        except (FileNotAnEnviHeader, EnviHeaderParsingError, MissingEnviHeaderParameter) as e:
            raise HypercubeHeaderInvalid(e)

        self._name = Path(path).stem
        self._wavelengths: np.ndarray | None = None
        self._wavelengths_unit: str | None = None

        if self._envi.bands.centers is not None:
            self._wavelengths = np.array(sorted(self._envi.bands.centers))
            self._wavelengths_unit = self._metadata.get("wavelength unit", None)

    @property
    def name(self) -> str:
        """Base name of the hyperspectral file (without extension)."""
        return self._name

    @property
    def metadata(self) -> dict[str, object]:
        """Metadata extracted from the ENVI header, as a dictionary."""
        return self._metadata

    @property
    def num_rows(self) -> int:
        """Number of spatial rows in the hyperspectral image."""
        return self._envi.nrows

    @property
    def num_cols(self) -> int:
        """Number of spatial columns in the hyperspectral image."""
        return self._envi.ncols

    @property
    def num_bands(self) -> int:
        """Number of spectral bands in the hyperspectral image."""
        return self._envi.nbands

    @property
    def bytes_per_sample(self) -> int:
        """Number of bytes used per spectral sample."""
        return self._envi.sample_size

    @property
    def num_samples(self) -> int:
        """Total number of spectral samples (pixels × bands)."""
        return self.num_rows * self.num_cols * self.num_bands

    @property
    def num_bytes(self) -> int:
        """Total size in bytes of the hyperspectral data."""
        return self.num_samples * self.bytes_per_sample

    @property
    def shape(self) -> tuple[int, int, int]:
        """Shape of the hyperspectral cube as (rows, columns, bands)."""
        return self._envi.shape

    @property
    def wavelengths(self) -> np.ndarray | None:
        """Sorted array of band center wavelengths, if available."""
        if self._wavelengths is not None:
            return self._wavelengths.copy()

        return None

    @property
    def wavelengths_unit(self) -> str | None:
        """Unit of the wavelengths if specified in the metadata."""
        return self._wavelengths_unit

    @property
    def default_bands(self) -> tuple[int, int, int]:
        """The default RGB band indices (if available, taken from metadata)."""
        try:
            red, green, blue = map(int, self._metadata["default bands"])
            return red, green, blue
        except (KeyError, TypeError):
            return self.num_bands - 1, self.num_bands // 2, 0

    def get_rgb(self, r: int, g: int, b: int) -> np.ndarray:
        """
        Extract an RGB image by assigning specified bands to the red, green, and blue channels.

        Parameters
        ----------
        r : int
            Band index for red channel.
        g : int
            Band index for green channel.
        b : int
            Band index for blue channel.

        Returns
        -------
        numpy.ndarray
            RGB image array of shape (rows, columns, 3).
        """
        return get_rgb(self._envi, (r, g, b))

    def get_grayscale(self, band: int) -> np.ndarray:
        """
        Extract a grayscale image from a single spectral band.

        Parameters
        ----------
        band : int
            Band index to use for grayscale image.

        Returns
        -------
        numpy.ndarray
            Grayscale image array of shape (rows, columns).
        """
        return get_rgb(self._envi, (band, band, band))

    def read_pixel(self, row: int, col: int) -> np.ndarray:
        """
        Read the spectral data of a single pixel.

        Parameters
        ----------
        row : int
            Row index of the pixel.
        col : int
            Column index of the pixel.

        Returns
        -------
        numpy.ndarray
            Spectrum of the pixel across all bands.
        """
        return self._envi.read_pixel(row, col)

    def read_pixels(self, points: list[tuple[int, int]]) -> np.ndarray:
        """
        Read spectra for multiple pixels.

        Parameters
        ----------
        points : list of tuple of int
            List of (row, col) tuples specifying pixel locations.

        Returns
        -------
        numpy.ndarray
            Array of spectra for each pixel.
        """
        return np.array([self.read_pixel(row, col) for row, col in points])

    def read_subregion(self, rows: tuple[int, int], cols: tuple[int, int], bands=None) -> np.ndarray:
        """
        Read a subregion of the hyperspectral cube.

        Parameters
        ----------
        rows : tuple of int
            Start and end row indices (inclusive, exclusive).
        cols : tuple of int
            Start and end column indices (inclusive, exclusive).
        bands : list or tuple or range, optional
            Bands to read. If None, reads all bands.

        Returns
        -------
        numpy.ndarray
            Hyperspectral data of the subregion.
        """
        return self._envi.read_subregion(rows, cols, bands)

    def read_subimage(self, rows, cols, bands=None) -> np.ndarray:
        """
        Read a rectangular subimage of the hyperspectral cube.

        Parameters
        ----------
        rows : list or tuple or range
            Row indices or slice.
        cols : list or tuple or range
            Column indices or slice.
        bands : list or tuple or range, optional
            Bands to read. If None, reads all bands.

        Returns
        -------
        numpy.ndarray
            Hyperspectral data of the subimage.
        """
        return self._envi.read_subimage(rows, cols, bands)

    def read_row(self, row: int, bands=None) -> np.ndarray:
        """
        Read all pixels in a given row.

        Parameters
        ----------
        row : int
            Row index to read.
        bands : list or tuple or range, optional
            Bands to read. If None, reads all bands.

        Returns
        -------
        numpy.ndarray
            Hyperspectral data of the row.
        """
        return self.read_subregion((row, row + 1), (0, self.num_cols), bands)

    def read_col(self, col: int, bands=None) -> np.ndarray:
        """
        Read all pixels in a given column.

        Parameters
        ----------
        col : int
            Column index to read.
        bands : list or tuple or range, optional
            Bands to read. If None, reads all bands.

        Returns
        -------
        numpy.ndarray
            Hyperspectral data of the column.
        """
        return self.read_subregion((0, self.num_rows), (col, col + 1), bands)


class HypercubeDataMissing(Exception):
    """Raised upon attempting to open a hypercube with a missing data file."""
    pass


class HypercubeHeaderInvalid(Exception):
    """Raised upon attempting to open a hypercube with a malformed header file."""
    pass
