import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class ColoringMode(QWidget):
    image_changed = Signal(np.ndarray)

    def reset(self):
        pass

    def activate(self):
        pass
