from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication


class ThemePixmap(QPixmap):
    def __init__(self, name):
        if Qt.ColorScheme.Dark == QApplication.styleHints().colorScheme():
            theme = "dark"
        else:
            theme = "light"

        super().__init__(f":/icons/{theme}/{name}")
