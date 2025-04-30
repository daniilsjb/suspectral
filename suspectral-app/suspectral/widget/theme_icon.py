from PySide6.QtGui import QIcon

from suspectral.widget.theme_pixmap import ThemePixmap


class ThemeIcon(QIcon):
    def __init__(self, name):
        super().__init__(ThemePixmap(name))
