import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class ColoringMode(QWidget):
    imageChanged = Signal(np.ndarray)
    statusChanged = Signal(bool)

    def start(self):
        pass
