from pathlib import Path

import numpy as np
import pandas as pd
import spectral as spy

import scipy.integrate as integrate
import scipy.interpolate as interpolate

from tqdm import tqdm


def main():
    imx219_df = pd.read_csv('resources/Sony_IMX219.csv')
    imx219_wavelengths = imx219_df['Wavelength'].values
    imx219_sensitivities = imx219_df[['R', 'G', 'B']].values
    imx219_splines = interpolate.CubicSpline(imx219_wavelengths, imx219_sensitivities)
    del imx219_df, imx219_wavelengths, imx219_sensitivities

    paths = list(Path('datasets/ICVL-HIRES').iterdir())
    paths = [p for p in paths if p.suffix == '.hdr']

    for path in tqdm(paths):
        if path.with_suffix('.npy').exists():
            continue

        envi = spy.io.envi.open(path)
        data = envi[:, 2:, 1:410].astype(np.float64) / 4095.0

        wavelengths = envi.bands.centers[1:410]
        imx219 = imx219_splines(wavelengths)
        imx219 /= np.max(integrate.simpson(imx219, wavelengths, axis=0))

        data = data.reshape(-1, data.shape[-1])

        image = np.column_stack((
            integrate.simpson(data * imx219[:, 0], wavelengths),
            integrate.simpson(data * imx219[:, 1], wavelengths),
            integrate.simpson(data * imx219[:, 2], wavelengths),
        ))

        with open(path.with_suffix('.npy'), 'wb') as file:
            np.save(file, image)

        del data, image, imx219


if __name__ == '__main__':
    main()
