from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import imageio.v3 as iio

import scipy.integrate as integrate
import scipy.interpolate as interpolate

from tqdm import tqdm


def main():
    wavelengths = np.arange(400, 700 + 1, 10)

    root = Path(__file__).parent.parent
    srf_df = pd.read_csv(root / 'resources' / 'sensitivities' / 'Sony_IMX219.csv')
    srf_w = srf_df['Wavelength'].values
    srf_r = interpolate.CubicSpline(srf_w, srf_df['R'].values)(wavelengths)
    srf_g = interpolate.CubicSpline(srf_w, srf_df['G'].values)(wavelengths)
    srf_b = interpolate.CubicSpline(srf_w, srf_df['B'].values)(wavelengths)
    del srf_df

    srf_r /= integrate.simpson(srf_r, wavelengths)
    srf_g /= integrate.simpson(srf_g, wavelengths)
    srf_b /= integrate.simpson(srf_b, wavelengths)

    paths = list((root / 'datasets' / 'ICVL-MATLAB').iterdir())
    paths = [p for p in paths if p.suffix == '.mat']

    for path in tqdm(paths):
        if path.with_suffix('.npy').exists():
            continue

        with h5py.File(path, 'r') as file:
            spectra = np.array(file['rad']).swapaxes(0, 2) / 4095.0

        image = np.dstack((
            integrate.simpson(spectra * srf_r, wavelengths),
            integrate.simpson(spectra * srf_g, wavelengths),
            integrate.simpson(spectra * srf_b, wavelengths),
        ))

        with open(path.with_suffix('.npy'), 'wb') as file:
            np.save(file, image)

        preview = (np.rot90(image) * 255).astype(np.uint8)
        iio.imwrite(path.with_suffix('.png'), preview)
        del spectra, image


if __name__ == '__main__':
    main()
