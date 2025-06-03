import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class ColoringMode(QWidget):
    """
    Defines the interface for conversion of hyperspectral data into RGB images.

    Signals
    -------
    imageChanged : Signal(np.ndarray)
        Emitted when a new RGB image is generated.
    statusChanged : Signal(bool)
        Indicates whether this mode is enabled for this hypercube.
    """

    imageChanged = Signal(np.ndarray)
    statusChanged = Signal(bool)

    def activate(self):
        """
        Activates the coloring mode.

        This method should be overridden by subclasses to initialize or enable
        any required functionality when the coloring mode becomes active.
        """
        pass

    def deactivate(self):
        """
        Deactivates the coloring mode.

        This method should be overridden by subclasses to clean up or disable
        any functionality when the coloring mode is no longer active.
        """
        pass
