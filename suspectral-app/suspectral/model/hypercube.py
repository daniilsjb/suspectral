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
        return self._name

    @property
    def metadata(self) -> dict[str, object]:
        return self._metadata

    @property
    def num_rows(self) -> int:
        return self._envi.nrows

    @property
    def num_cols(self) -> int:
        return self._envi.ncols

    @property
    def num_bands(self) -> int:
        return self._envi.nbands

    @property
    def bytes_per_sample(self) -> int:
        return self._envi.sample_size

    @property
    def num_samples(self) -> int:
        return self.num_rows * self.num_cols * self.num_bands

    @property
    def num_bytes(self) -> int:
        return self.num_samples * self.bytes_per_sample

    @property
    def shape(self) -> tuple[int, int, int]:
        return self._envi.shape

    @property
    def wavelengths(self) -> np.ndarray | None:
        if self._wavelengths is not None:
            return self._wavelengths.copy()

        return None

    @property
    def wavelengths_unit(self) -> str | None:
        return self._wavelengths_unit

    @property
    def default_bands(self) -> tuple[int, int, int]:
        try:
            red, green, blue = map(int, self._metadata["default bands"])
            return red, green, blue
        except (KeyError, TypeError):
            return self.num_bands - 1, self.num_bands // 2, 0

    def get_rgb(self, r: int, g: int, b: int) -> np.ndarray:
        return get_rgb(self._envi, (r, g, b))

    def get_grayscale(self, band: int) -> np.ndarray:
        return get_rgb(self._envi, (band, band, band))

    def read_pixel(self, row: int, col: int) -> np.ndarray:
        return self._envi.read_pixel(row, col)

    def read_pixels(self, points: list[tuple[int, int]]) -> np.ndarray:
        return np.array([self.read_pixel(row, col) for row, col in points])

    def read_subregion(self, rows: tuple[int, int], cols: tuple[int, int], bands=None) -> np.ndarray:
        return self._envi.read_subregion(rows, cols, bands)

    def read_subimage(self, rows, cols, bands=None) -> np.ndarray:
        return self._envi.read_subimage(rows, cols, bands)


class HypercubeDataMissing(Exception):
    """Raised upon attempting to open a hypercube with a missing data file."""
    pass


class HypercubeHeaderInvalid(Exception):
    """Raised upon attempting to open a hypercube with a malformed header file."""
    pass
