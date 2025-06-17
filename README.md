<div align="center">
  <img src="https://github.com/user-attachments/assets/4847f508-03ac-42e1-ad1b-d2eef5533373" width="100" alt="Suspectral">
  <h1>Suspectral</h1>
  <div>Visualization and reconstruction of hyperspectral imaging data</div>
  <div>from RGB images based on spectral response functions.</div>
</div>

## Features

- Support for hyperspectral images in the ENVI format. 📂
- Sensor-based synthesis of RGB images from hypercubes. 🖼️
- Preview of sRGB images based on the CIE XYZ 1931 CMFs. 👁️
- Options for performing color correction on synthetic images. 🎨
- Ability to display pixel spectra either individually or in groups. 📈
- Export of spectral data into CSV, MATLAB, and NumPy tabular files. 📝
- Saving image previews and spectral plots into PNG, JPG, TIFF, and BMP. 📷
- Transformations for image preview: zooming, panning, rotations, flips. 🔄️
- Automatic detection of the operating system's light and dark themes. 🔥

## Running / Building

This repository contains two subprojects: [suspectral-app](./suspectral-app) and [suspectral-notebook](./suspectral-notebook).
Both projects are intended to be run separately, each in its own [virtual environment](https://docs.python.org/3/library/venv.html), if needed.

### suspectral-app

This subproject contains the software application developed using [PySide6](https://doc.qt.io/qtforpython-6/gettingstarted.html#getting-started) bindings for the [Qt](https://www.qt.io/) framework.
To run the software, simply follow these steps from the [suspectral-app](./suspectral-app) directory, assuming you have already activated its virtual environment:

1. `pip install -r requirements.txt`
2. `pyside6-rcc resources/resources.qrc -o resources.py`
3. `py app.py`

To run automated tests using [pytest](https://docs.pytest.org/en/stable/), simply execute one of the following commands:

- `pytest tests` (without coverage)
- `pytest tests --cov=suspectral` (with coverage)

The software can be packaged into a Windows executable using [PyInstaller](https://github.com/pyinstaller/pyinstaller):

1. `pyinstaller app.spec`

To create an installation wizard via [Inno Setup](https://jrsoftware.org/isinfo.php), use the provided [compilation script](./suspectral-app/installer/Windows.iss).

### suspectral-notebook

This subproject contains the [Jupyter](https://jupyter.org/) notebooks contain various experiments and demonstrations revolving around image synthesis and spectral reconstruction.
To run the notebooks, simply follow these steps from the [suspectral-notebook](./suspectral-notebook) directory, assuming you have already activated its virtual environment:

1. `pip install -r requirements.txt`
2. `jupyter notebook`

You must download datasets from their respective authors and extract them in corresponding [datasets](./suspectral-notebook/datasets) directories:

- [ICVL](https://icvl.cs.bgu.ac.il/pages/researches/hyperspectral-imaging.html). Arad, B. and Ben-Shahar, O., 2016. Sparse recovery of hyperspectral signal from natural RGB images. In Computer Vision–ECCV 2016: 14th European Conference, Amsterdam, The Netherlands, October 11–14, 2016, Proceedings, Part VII 14 (pp. 19-34). Springer International Publishing.
- [CAVE](https://cave.cs.columbia.edu/repository/Multispectral). Yasuma, F., Mitsunaga, T., Iso, D. and Nayar, S.K., 2010. Generalized assorted pixel camera: postcapture control of resolution, dynamic range, and spectrum. IEEE transactions on image processing, 19(9), pp.2241-2253.
- [KAUST](https://hdl.handle.net/10754/670368). Li, Y., Fu, Q. and Heidrich, W., 2021. Multispectral illumination estimation using deep unrolling network. In Proceedings of the IEEE/CVF international conference on computer vision (pp. 2672-2681).
- [Harvard](https://vision.seas.harvard.edu/hyperspec/). Chakrabarti, A. and Zickler, T., 2011, June. Statistics of real-world hyperspectral images. In CVPR 2011 (pp. 193-200). IEEE.

To convert the hyperspectral images into a format that is compatible with the software, use the [hsi2envi.py](./suspectral-notebook/scripts/hsi2envi.py) script.

> [!NOTE]
> The [ICVL-MATLAB](./suspectral-notebook/datasets/ICVL-MATLAB) directory is intended for the downsampled images with `.mat` extension, whereas the [ICVL-ENVI-RAW](./suspectral-notebook/datasets/ICVL-ENVI-RAW)
> is intended for the original output of the hyperspectral camera with paired `.hdr`/`.raw` files. The directory [ICVL-ENVI](./suspectral-notebook/datasets/ICVL-ENVI) should be populated by manually downsampled
> images using the [resample_icvl.py](./suspectral-notebook/scripts/resample_icvl.py) script.

To prepare the datasets for training of spectral reconstruction models, use the [synthesize_cave.py](./suspectral-notebook/scripts/synthesize_cave.py),
[synthesize_icvl_envi.py](./suspectral-notebook/scripts/synthesize_icvl_envi.py), and [synthesize_icvl_matlab.py](./suspectral-notebook/scripts/synthesize_icvl_matlab.py)
scripts (other datasets were only used for software testing).

## License

MIT, Copyright © 2025, Daniils Buts
