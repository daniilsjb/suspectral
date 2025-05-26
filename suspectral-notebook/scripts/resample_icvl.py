import argparse
import warnings
from pathlib import Path

import numpy as np
import spectral as spy
import scipy.interpolate as interpolate
from tqdm import tqdm


def resample(path: Path):
    envi = spy.io.envi.open(path)

    old_wavelengths = np.array(envi.bands.centers)
    new_wavelengths = np.arange(400, 1000 + 1, 5)
    metadata = {
        'default bands': [48, 30, 12],
        'wavelength': new_wavelengths,
        'wavelength unit': 'nm',
    }

    # Note that we remove the leftmost two columns because they contain garbage.
    image = np.empty((envi.nrows, envi.ncols - 2, len(new_wavelengths)))
    for row in range(envi.nrows):
        data = envi.read_subregion((row, row + 1), (2, envi.ncols))
        data = data.reshape(-1, envi.nbands).T

        splines = interpolate.CubicSpline(old_wavelengths, data)
        image[row, :, :] = splines(new_wavelengths).T

    image = np.rint(image).astype(np.uint16)
    spy.envi.save_image(path, image, ext='raw', force=True, metadata=metadata)

    del envi, image


def main():
    parser = argparse.ArgumentParser(
        description='Resample hyperspectral images from the original ICVL dataset to downscale.',
    )
    parser.add_argument(
        '--path',
        type=Path,
        help='Path to the directory containing unprocessed ICVL images.',
        required=True,
    )

    args = parser.parse_args()
    if not args.path.is_dir():
        parser.error(f'The path {args.path} is not a valid directory.')

    warnings.filterwarnings('ignore')
    for file in tqdm(list(args.path.glob('*.hdr'))):
        resample(file)


if __name__ == '__main__':
    main()
