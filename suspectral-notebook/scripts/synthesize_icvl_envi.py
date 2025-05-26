from pathlib import Path

import numpy as np
import pandas as pd
import spectral as spy
import imageio.v3 as iio

import scipy.integrate as integrate
import scipy.interpolate as interpolate

from tqdm import tqdm


def main():
    wavelengths = np.arange(400, 1000 + 1, 5)
    wavelengths_mask = wavelengths <= 700
    wavelengths = wavelengths[wavelengths_mask]

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

    paths = (root / 'datasets' / 'ICVL-ENVI').iterdir()
    paths = [p for p in paths if p.suffix == '.hdr']

    for path in tqdm(paths):
        if path.with_suffix('.npy').exists():
            continue

        envi = spy.io.envi.open(path)

        image = np.zeros((envi.nrows, envi.ncols, 3))
        for row in range(envi.nrows):
            spectra = envi.read_subregion((row, row + 1), (0, envi.ncols)).astype(np.float64)
            spectra = spectra[:, :, wavelengths_mask] / 4095.0

            image[row, :, 0] = integrate.simpson(spectra * srf_r, wavelengths)
            image[row, :, 1] = integrate.simpson(spectra * srf_g, wavelengths)
            image[row, :, 2] = integrate.simpson(spectra * srf_b, wavelengths)

        image[image < 0] = 0
        image[image > 1] = 1

        with open(path.with_suffix('.npy'), 'wb') as file:
            np.save(file, image)

        preview = (np.rot90(image) * 255).astype(np.uint8)
        iio.imwrite(path.with_suffix('.png'), preview)
        del image


if __name__ == '__main__':
    main()
