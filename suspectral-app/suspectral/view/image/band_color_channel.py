from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QSpinBox, QSlider, QHBoxLayout, QLabel


class BandColorChannel(QWidget):
    """
    A widget combining a slider and a spin box for selecting a band index for a color channel.

    Signals
    -------
    valueChanged(int)
        Emitted when the selected band value changes, either via the spin box or the slider.

    Parameters
    ----------
    name : str, optional
        Label to display before the slider (e.g., "Red", "Green", "Blue").
    parent : QWidget or None, optional
        The parent QWidget of this widget, by default None.
    """

    valueChanged = Signal(int)

    def __init__(self, name: str | None = None, parent: QWidget | None = None):
        super().__init__(parent)

        self.spinbox = QSpinBox(self)
        self.spinbox.valueChanged.connect(self._on_spinbox_update)

        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.sliderReleased.connect(self._on_slider_update)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        layout = QHBoxLayout()
        if name is not None:
            layout.addWidget(QLabel(name))
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)

        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def reset(self, minimum: int, maximum: int, value: int, suffix: str = ""):
        """
        Configure the range and initial value for both the slider and the spin box.

        Parameters
        ----------
        minimum : int
            The minimum allowed value.
        maximum : int
            The maximum allowed value.
        value : int
            The initial value to set in both controls.
        suffix : str, optional
            Suffix (e.g., unit or symbol) to display in the spin box.
        """

        self.slider.blockSignals(True)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.slider.setTickInterval((maximum - minimum) // 10)
        self.slider.blockSignals(False)

        self.spinbox.blockSignals(True)
        self.spinbox.setRange(minimum, maximum)
        self.spinbox.setValue(value)
        self.spinbox.setSuffix(suffix)
        self.spinbox.blockSignals(False)

    def _on_slider_update(self):
        value = self.slider.value()
        self.spinbox.setValue(value)

    def _on_spinbox_update(self, value: int):
        self.slider.setValue(value)
        self.valueChanged.emit(value)
