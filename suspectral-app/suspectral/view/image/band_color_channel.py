from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QSpinBox, QSlider, QHBoxLayout, QLabel


class BandColorChannel(QWidget):
    valueChanged = Signal(int)

    def __init__(self, name: str | None = None):
        super().__init__()

        self.spinbox = QSpinBox()
        self.spinbox.valueChanged.connect(self._on_spinbox_update)

        self.slider = QSlider(Qt.Orientation.Horizontal)
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
