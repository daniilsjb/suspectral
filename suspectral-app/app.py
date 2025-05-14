import sys

import pyqtgraph as pg
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from suspectral.suspectral import Suspectral

import resources
assert resources

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationVersion("0.0.1")

    palette = app.palette()
    pg.setConfigOptions(
        background=palette.color(QPalette.ColorRole.Base).name(),
        foreground=palette.color(QPalette.ColorRole.WindowText).name(),
    )

    window = Suspectral()
    window.show()

    sys.exit(app.exec())
