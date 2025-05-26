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
- Ability to display pixel spectra either individually or in groups. 📈
- Export of spectral data into CSV, MATLAB, and NumPy tabular files. 📝
- Saving image previews and spectral plots into PNG, JPG, TIFF, and BMP. 📷
- Transformations for image preview: zooming, panning, rotations, flips. 🔄️
- Automatic detection of the operating system's light and dark themes. 🔥

## Running

This repository contains two subprojects: [suspectral-app](./suspectral-app) and [suspectral-notebook](./suspectral-notebook).
Both projects are intended to be run separately, each in its own [virtual environment](https://docs.python.org/3/library/venv.html), if needed.

### Application

The application is implemented using [PySide6](https://doc.qt.io/qtforpython-6/gettingstarted.html#getting-started) bindings for the [Qt](https://www.qt.io/) framework.
To run the software, simply follow these steps from the [suspectral-app](./suspectral-app) directory (assuming you have already activated a virtual environment):

```shell
# Install all necessary dependencies.
pip install -r requirements.txt

# Compile software resources (e.g., icons).
pyside6-rcc resources/resources.qrc -o resources.py

# Launch the application.
py app.py
```

To run automated tests using [pytest](https://docs.pytest.org/en/stable/), simply execute one of the following commands:

```shell
# To run tests without test coverage.
pytest tests

# To run tests with test coverage.
pytest --cov=suspectral tests
```

### Notebooks

The [Jupyter](https://jupyter.org/) notebooks contain various experiments and demonstrations revolving around image synthesis and spectral reconstruction.
To run the notebooks, simply follow these steps from the [suspectral-notebook](./suspectral-notebook) directory (assuming you have already activated a virtual environment):

```shell
# Install all necessary dependencies.
pip install -r requirements.txt

# Launch the Jupyter notebook server.
jupyter notebook
```

## Packaging

The software can be packaged into a Windows executable using [PyInstaller](https://github.com/pyinstaller/pyinstaller):

```shell
pyinstaller app.spec
```

To create an installation wizard for the executable through [Inno Setup](https://jrsoftware.org/isinfo.php), you may use the provided [compilation script](./suspectral-app/installer/Windows.iss).

## License

MIT, Copyright © 2025, Daniils Buts
