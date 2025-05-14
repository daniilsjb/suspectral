from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication


class ThemePixmap(QPixmap):
    def __init__(self, name):
        theme = "dark" if Qt.ColorScheme.Dark == QApplication.styleHints().colorScheme() else "light"
        super().__init__(f":/icons/{theme}/{name}")
