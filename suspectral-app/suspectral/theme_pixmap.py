from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication


class ThemePixmap(QPixmap):
    """
    A QPixmap that automatically loads a themed icon based on the application's current color scheme.

    This class dynamically selects between light and dark icon variants depending on whether the
    application's active `Qt.ColorScheme` is `Dark` or `Light`. It assumes that themed icons are located
    at resource paths in the format `:/icons/{theme}/{name}`.

    Parameters
    ----------
    name : str
        The base name of the icon file (without path), which will be prefixed according to the
        current theme (e.g., `:/icons/dark/{name}` or `:/icons/light/{name}`).
    """

    def __init__(self, name):
        theme = "dark" if Qt.ColorScheme.Dark == QApplication.styleHints().colorScheme() else "light"
        super().__init__(f":/icons/{theme}/{name}")
