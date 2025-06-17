import os
from pathlib import Path

import numpy as np
import pandas as pd
import imageio.v3 as iio
import spectral as spy

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

    paths = list((root / 'datasets' / 'CAVE').iterdir())
    paths = [p for p in paths if p.is_dir()]

    for path in tqdm(paths):
        if path.with_suffix('.npy').exists():
            continue

        with os.scandir(path) as files:
            bands = []
            for f in files:
                if f.name.endswith('.png'):
                    band = iio.imread(f.path)
                    band = band / np.iinfo(band.dtype).max
                    if band.ndim == 3:
                        band = band[:, :, 0]
                    bands.append(band)

        # Note that we remove the leftmost four columns because they contain garbage.
        spectra = np.dstack(bands)
        spectra = spectra[:, 4:, :]

        image = np.dstack((
            integrate.simpson(spectra * srf_r, wavelengths),
            integrate.simpson(spectra * srf_g, wavelengths),
            integrate.simpson(spectra * srf_b, wavelengths),
        ))

        metadata = {
            'wavelength unit': 'nm',
            'wavelength': f'{{\n{",\n".join(f"\t{w}" for w in wavelengths)}\n}}',
        }

        hdr = path.with_suffix('.hdr')
        spy.envi.save_image(hdr, spectra, ext='raw', metadata=metadata, force=True)

        with open(path.with_suffix('.npy'), 'wb') as file:
            np.save(file, image)

        preview = (image * 255).astype(np.uint8)
        iio.imwrite(path.with_suffix('.png'), preview)
        del spectra, image


if __name__ == '__main__':
    main()
