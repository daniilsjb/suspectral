import argparse
import warnings
from pathlib import Path

import numpy as np
import scipy.interpolate as interpolate
import spectral as spy
from tqdm import tqdm


def preprocess(path: Path):
    envi = spy.io.envi.open(path)

    old_bands = np.array(envi.bands.centers)
    new_bands = np.arange(400, 1000 + 1, 5)

    result = np.empty((envi.nrows, envi.ncols - 2, len(new_bands)))
    for row in range(envi.nrows):
        data = envi.read_subregion((row, row + 1), (2, envi.ncols))
        data = data.reshape(-1, envi.nbands).T

        splines = interpolate.CubicSpline(old_bands, data)
        result[row, :, :] = splines(new_bands).T

    del envi

    result = np.rint(result).astype(np.uint16)
    spy.envi.save_image(path, result, ext='raw', force=True, metadata={
        'default bands': [48, 30, 12],
        'wavelength': new_bands,
        'wavelength unit': 'nm',
    })

    del result


def main():
    parser = argparse.ArgumentParser(
        description='Preprocess hyperspectral images from the original ICVL dataset.',
    )
    parser.add_argument(
        '--path',
        type=Path,
        required=True,
        help='Path to the directory containing unprocessed ICVL images.'
    )

    args = parser.parse_args()
    if not args.path.is_dir():
        parser.error(f'The path {args.path} is not a valid directory.')

    warnings.filterwarnings('ignore')
    for file in tqdm(list(args.path.glob('*.hdr'))):
        preprocess(file)


if __name__ == '__main__':
    main()
