from PySide6.QtWidgets import QWidget

from suspectral.view.status.status_view_item import StatusViewItem
from suspectral.theme_pixmap import ThemePixmap


class ShapeStatus(StatusViewItem):
    """
    A widget that displays the shape of a hyperspectral datacube.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget, if any.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(ThemePixmap("shape.svg"), parent)

    def set(self, num_cols: int, num_rows: int, num_bands: int):
        """
        Update the displayed shape of the hyperspectral cube.

        Parameters
        ----------
        num_cols : int
            Number of columns (width) in the data.
        num_rows : int
            Number of rows (height) in the data.
        num_bands : int
            Number of spectral bands in the data.
        """
        self._label.setText(f"{num_cols} × {num_rows} × {num_bands}")
