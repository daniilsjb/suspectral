from pathlib import Path

import h5py
import numpy as np
import pandas as pd

import scipy.integrate as integrate
import scipy.interpolate as interpolate

from tqdm import tqdm


def main():
    hsi_wavelengths = np.arange(400, 700 + 1, 10)

    parent = Path('.').parent
    imx219_df = pd.read_csv(parent / 'resources' / 'Sony_IMX219.csv')
    imx219_df = imx219_df.iloc[::5]

    imx219_wavelengths = imx219_df['Wavelength'].values
    imx219_sensitivity = imx219_df[['R', 'G', 'B']].values
    del imx219_df

    wavelength_min = max(hsi_wavelengths.min(), imx219_wavelengths.min())
    wavelength_max = min(hsi_wavelengths.max(), imx219_wavelengths.max())
    wavelength_mask = ((imx219_wavelengths >= wavelength_min) & (imx219_wavelengths <= wavelength_max))

    imx219_wavelengths = imx219_wavelengths[wavelength_mask]
    imx219_sensitivity = imx219_sensitivity[wavelength_mask]

    imx219_sensitivity_total = integrate.simpson(imx219_sensitivity, imx219_wavelengths, axis=0)
    imx219_sensitivity /= np.max(imx219_sensitivity_total)

    imx219_r = imx219_sensitivity[:, 0]
    imx219_g = imx219_sensitivity[:, 1]
    imx219_b = imx219_sensitivity[:, 2]

    paths = list((parent / 'datasets' / 'ICVL-MATLAB').iterdir())
    paths = [p for p in paths if p.suffix == '.mat']

    for path in tqdm(paths):
        if path.with_suffix('.npy').exists():
            continue

        with h5py.File(path, 'r') as file:
            hsi = np.array(file['rad']).swapaxes(0, 2) / 4095

        height, width, bands = hsi.shape
        hsi_splines = interpolate.CubicSpline(hsi_wavelengths, hsi.reshape(-1, bands).T)
        hsi = hsi_splines(imx219_wavelengths).T.reshape(height, width, -1)
        del hsi_splines

        image = np.dstack((
            integrate.simpson(hsi * imx219_r, imx219_wavelengths),
            integrate.simpson(hsi * imx219_g, imx219_wavelengths),
            integrate.simpson(hsi * imx219_b, imx219_wavelengths),
        ))

        with open(path.with_suffix('.npy'), 'wb') as file:
            np.save(file, image)

        del hsi, image


if __name__ == '__main__':
    main()
