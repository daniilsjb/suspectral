from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

HTML_HEADER = """
<html>
  <head>
    <style>
      body {{
        margin: 4px;
      }}
    </style>
  </head>
  <body>
"""

HTML_FOOTER = """
  </body>
</html>
"""

HTML_INTRODUCTION = """
<h1>Suspectral</h1>
<p>
  Software for interactive visualization and extraction of hyperspectral imaging data and metadata stored in the ENVI format.
  Hypercubes can be visualized either through direct assignment of individual spectral bands to color channels of the image
  or via synthesis using spectral sensitivities.
</p>
"""

HTML_IMAGE_VIEW = """
<h2>Image View</h2>
<p>
  The central area of the window is the view into the scene containing the visualized hypercube. The image may be transformed
  by zooming, panning, rotating, and flipping. Through its context menu, the image can be either copied to the clipboard
  or saved to a file. All other interactions with the image are defined by the currently selected tool.
</p>
"""

HTML_TOOLS = """
<h3>Tools</h3>
<table border="1" cellspacing="0" cellpadding="4" width="100%" style="margin-top: 8px;">
  <thead>
    <tr>
      <th width="40">Icon</th>
      <th width="60">Name</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="vertical-align: middle;"><img src=":/icons/{theme}/cursor.svg"></td>
      <td style="vertical-align: middle;">Cursor</td>
      <td>Ordinary cursor with no additional functionality.</td>
    </tr>
    <tr>
      <td style="vertical-align: middle;"><img src=":/icons/{theme}/pan.svg"></td>
      <td style="vertical-align: middle;">Pan</td>
      <td>
        Allows panning the image by holding down the left mouse button while moving the cursor around.
        The boundaries are restricted only to the image area.
      </td>
    </tr>
    <tr>
      <td style="vertical-align: middle;"><img src=":/icons/{theme}/hand-point.svg"></td>
      <td style="vertical-align: middle;">Inspect</td>
      <td>
        Allows selecting individual pixels for plotting, each marked on the image view with a
        distinct color. Multiple pixels may be selected simultaneously by holding down the Ctrl key.
        The selected pixels can be exported via the context menu.
      </td>
    </tr>
    <tr>
      <td style="vertical-align: middle;"><img src=":/icons/{theme}/select.svg"></td>
      <td style="vertical-align: middle;">Select Area</td>
      <td>
        Allows selecting a rectangular region of pixels. Several equally spaced pixels are automatically
        selected for plotting, each marked on the image view with a distinct color. The pixels and the
        entire area can be exported via the context menu.
      </td>
    </tr>
    <tr>
      <td style="vertical-align: middle;"><img src=":/icons/{theme}/zoom.svg"></td>
      <td style="vertical-align: middle;">Zoom</td>
      <td>
        Allows zooming in by clicking the left mouse button and zooming out by clicking the right mouse button.
        The context menu is unavailable for this tool.
      </td>
    </tr>
  </tbody>
</table>
"""

HTML_METADATA_VIEW = """
<h2>Metadata</h2>
<p>
  The Metadata area displays the contents of the hypercube's header file in tabular format. The metadata
  fields are defined by the author of the image and are simply displayed as-is. 
</p>
"""

HTML_SELECTION_VIEW = """
<h2>Selection</h2>
<p>
  The Selection area displays the legend for the currently selected pixels, either individually or
  through the rectangular selection tool. Each pixel is identified by a color and its spatial coordinates.
</p>
"""

HTML_SPECTRAL_VIEW = """
<h2>Spectral Plot</h2>
<p>
  The Spectral Plot area displays the spectra of the currently selected pixels, either individually or
  through the rectangular selection tool. The plot can be copied to clipboard or saved to a file via
  the context menu. Additionally, the plotted spectra can be exported.
</p>
"""

HTML_IMAGE_CONTROLS = """
<h2>Image Controls</h2>
<p>The Image Controls area provides several modes for visualization of the hypercube.</p>

<h3>Band Coloring (RGB)</h3>
<p>In this mode, three spectral bands of the hypercube are assigned to the red, green, and blue channels
  of the image, respectively. If the metadata specifies the default bands of the image, they are used as
  initial values. Otherwise, the last, middle, and first bands are used instead. The bands may be indexed either
  by their band number or by wavelengths of the spectral bands. The latter is only supported if the hypercube's
  metadata contains the wavelengths field.
</p>

<h3>Band Coloring (Grayscale)</h3>
<p>In this mode, a single spectral band of the hypercube is used to display a grayscale image. The bands may be indexed either
  by their band number or by wavelengths of the spectral bands. The latter is only supported if the hypercube's
  metadata contains the wavelengths field.
</p>

<h3>True Coloring (CIE 1931)</h3>
<p>In this mode, the RGB image is synthetically produced using the CIE 1931 color matching functions. Several configuration
  options are provided to customize the output:
</p>
<p><strong>Illuminant.</strong> If specified, this spectrum will be interpreted as the spectral power distribution
  of the scene illuminant, which may affect the colour temperature of the image. Must be a CSV file containing two columns:
  Wavelength and Intensity. Alternatively, may be selected from multiple preset options.
<p><strong>White.</strong> If specified, the spectrum of this pixel will be used to approximate the spectral
  power distribution of the scene illuminant, making it the brightest in the image. The available options are the currently
  selected pixels using Inspect or Select Area tools.
<p><strong>Black.</strong> If specified, the spectrum of this pixel will be used to approximate the spectral
  bias of the imaging spectrometer device, making it the darkest in the image. The available options are the currently
  selected pixels using Inspect or Select Area tools.
<p><strong>Apply sRGB conversion.</strong> If enabled, the synthesized image will be transformed using the standard matrix
  for conversion from CIE XYZ (1931) tristimulus values to the sRGB (D65) space.
<p><strong>Apply gamma encoding.</strong> If enabled, the standard CIE sRGB gamma encoding function will be applied to
  the synthesized RGB image, which corrects its brightness if linear light is used.
<p><strong>Apply per-channel contrast.</strong> If enabled, each color channel of the synthesized RGB image will be separately
  normalized by subtracting its minimum value and dividing by its maximum value.

<h3>True Coloring (Sony IMX219)</h3>
<p>In this mode, the RGB image is synthetically produced using the spectral response functions of the Sony IMX219 camera.
  Several configuration options are provided to customize the output:
</p>
<p><strong>Sensor SRF.</strong> These spectra will be interpreted as the red, green, and blue spectral response
  functions of the sensor, which describe its sensitivity to light. Must be a CSV file containing columns Wavelength, R, G, and B.
  Alternatively, may be selected from multiple preset options.
<p><strong>Illuminant.</strong> If specified, this spectrum will be interpreted as the spectral power distribution
  of the scene illuminant, which may affect the colour temperature of the image. Must be a CSV file containing two columns:
  Wavelength and Intensity. Alternatively, may be selected from multiple preset options.
<p><strong>White.</strong> If specified, the spectrum of this pixel will be used to approximate the spectral
  power distribution of the scene illuminant, making it the brightest in the image. The available options are the currently
  selected pixels using Inspect or Select Area tools.
<p><strong>Black.</strong> If specified, the spectrum of this pixel will be used to approximate the spectral
  bias of the imaging spectrometer device, making it the darkest in the image. The available options are the currently
  selected pixels using Inspect or Select Area tools.
<p><strong>Apply per-channel contrast.</strong> If enabled, each color channel of the synthesized RGB image will be separately
  normalized by subtracting its minimum value and dividing by its maximum value.
"""

HTML_EXPORTING = """
<h2>Exporting</h2>
<p>The spectra of the selected pixels may be exported in several ways:</p>
<p><strong>Clipboard.</strong> The spectra are copied to the system's clipboard as text in the CSV format, separated by tabs.
  If present, the corresponding wavelengths are included in the output.                    
</p>
<p><strong>CSV.</strong> The spectra are saved to the selected file as text in the CSV format, separated by tabs.
  If present, the corresponding wavelengths are included in the output.                    
</p>
<p><strong>MATLAB.</strong> The spectra are saved as a MATLAB file containing two variables: spectra and wavelengths (if present).
  The spectral matrix is of shape (N × M), where N is the number of selected pixels and M is the number of spectral bands in the hypercube.
</p>
<p><strong>NumPy.</strong> The spectra are saved as a NumPy array file containing the spectra and wavelengths (if present) as a single
  multidimensional array of shape (N × M), N is the number of selected pixels (+ 1 if wavelengths are present) and M is the number of
  spectral bands in the hypercube.
</p>
"""

HTML_SHORTCUTS = """
<h2>Keyboard Shortcuts</h2>
<table border="1" cellspacing="0" cellpadding="4" width="100%" style="margin-top: 8px;">
  <thead>
    <tr>
      <th width="100">Shortcut</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Ctrl + O</td><td>Open a hypercube.</td></tr>
    <tr><td>Ctrl + W</td><td>Close the hypercube.</td></tr>
    <tr><td>Ctrl + Q</td><td>Quit the program.</td></tr>
    <tr><td>Ctrl + Plus</td><td>Zoom the image in.</td></tr>
    <tr><td>Ctrl + Minus</td><td>Zoom the image out.</td></tr>
    <tr><td>Ctrl + 1</td><td>Zoom the image to fit.</td></tr>
    <tr><td>Ctrl + A</td><td>Rotate the image left.</td></tr>
    <tr><td>Ctrl + D</td><td>Rotate the image right.</td></tr>
    <tr><td>Ctrl + V</td><td>Flip the image vertically.</td></tr>
    <tr><td>Ctrl + H</td><td>Flip the image horizontally.</td></tr>
  </tbody>
</table>
"""


class HelpDialog(QDialog):
    """
    A dialog window that displays help content in HTML format.

    The dialog uses a QTextBrowser widget to render the help text, adapts the theme
    (dark or light) based on the application's current color scheme, and provides
    an OK button to close the dialog.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget of the dialog, by default None.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setMinimumSize(600, 400)
        self.resize(600, 400)

        scheme = QApplication.styleHints().colorScheme()
        theme = "dark" if scheme == Qt.ColorScheme.Dark else "light"

        text = QTextBrowser()
        text.setHtml(
            HTML_HEADER
            + HTML_INTRODUCTION
            + HTML_IMAGE_VIEW
            + HTML_TOOLS.format(theme=theme)
            + HTML_METADATA_VIEW
            + HTML_SELECTION_VIEW
            + HTML_SPECTRAL_VIEW
            + HTML_IMAGE_CONTROLS
            + HTML_EXPORTING
            + HTML_SHORTCUTS
            + HTML_FOOTER
        )

        okay = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        okay.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(text)
        layout.addWidget(okay)
