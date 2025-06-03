from PySide6.QtGui import QIcon

from suspectral.theme_pixmap import ThemePixmap


class ThemeIcon(QIcon):
    """
    A QIcon that automatically uses a themed pixmap based on the application's color scheme.

    This class constructs an icon by wrapping a `ThemePixmap`, allowing for automatic
    adaptation to light or dark mode themes using Qt's `ColorScheme`.

    Parameters
    ----------
    name : str
        The base name of the icon file (e.g., "edit.png"). The actual resource path
        will be resolved via `ThemePixmap`, depending on the current color scheme.
    """

    def __init__(self, name):
        super().__init__(ThemePixmap(name))
