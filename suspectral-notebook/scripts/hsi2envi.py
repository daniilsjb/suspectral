import os
import argparse
from pathlib import Path

import h5py
import numpy as np
import scipy.io as sio
import imageio.v3 as iio
from spectral import envi

parent = Path('.').parent


def extract_icvl(name: str):
    with h5py.File(parent / 'datasets' / 'ICVL' / f'{name}.mat', 'r') as file:
        datacube = np.array(file['rad']).swapaxes(0, 2)
        wavelengths = np.squeeze(file['bands'])

    return datacube, wavelengths


def extract_cave(name: str):
    with os.scandir(parent / 'datasets' / 'CAVE' / name) as files:
        bands = list(iio.imread(f.path) for f in files if f.name.endswith('.png'))

    datacube = np.dstack(bands) / np.iinfo(np.uint16).max
    wavelengths = np.arange(400, 700 + 1, 10)
    return datacube, wavelengths


def extract_kaust(name: str):
    with h5py.File(parent / 'datasets' / 'KAUST' / f'{name}.h5', 'r') as file:
        datacube = np.array(file['img\\']).swapaxes(0, 2)
        wavelengths = np.arange(400, 730 + 1, 10)

    return datacube, wavelengths


def extract_harvard(name: str):
    datacube = sio.loadmat(str(parent / 'datasets' / 'Harvard' / f'{name}.mat'))['ref']
    wavelengths = np.arange(420, 720 + 1, 10)
    return datacube, wavelengths


def main():
    parser = argparse.ArgumentParser(
        description='Convert hyperspectral images to the ENVI format.',
    )
    parser.add_argument(
        '--dataset',
        required=True,
        choices=['icvl', 'cave', 'kaust', 'harvard'],
        help='Name of the dataset that contains the hyperspectral image.'
    )
    parser.add_argument(
        '--name',
        required=True,
        help='Name of the hyperspectral image to be converted, without extension.'
    )
    parser.add_argument(
        '--destination',
        help='Path to the directory where the resulting image is to be saved.',
        default='.',
    )

    args = parser.parse_args()
    match args.dataset:
        case 'icvl':
            datacube, wavelengths = extract_icvl(args.name)
        case 'cave':
            datacube, wavelengths = extract_cave(args.name)
        case 'kaust':
            datacube, wavelengths = extract_kaust(args.name)
        case 'harvard':
            datacube, wavelengths = extract_harvard(args.name)
        case _:
            raise Exception(f'Unknown dataset: {args.dataset}')

    wavelengths = ',\n'.join(f'\t{w}' for w in wavelengths)
    metadata = {
        'wavelength unit': 'nm',
        'wavelength': f'{{\n{wavelengths}\n}}',
    }

    hdr = Path(args.destination) / f'{args.name}.hdr'
    envi.save_image(hdr, datacube, ext='raw', metadata=metadata, force=True)


if __name__ == '__main__':
    main()
