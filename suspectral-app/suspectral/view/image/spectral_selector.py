import os
from io import BytesIO
from typing import cast

import numpy as np
from PySide6.QtCore import QEvent, QPoint, QResource, QObject, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QWidget,
)


class SpectralSelector(QWidget):
    """
    A widget for selecting spectral reference data from either predefined presets
    or user-provided CSV files.

    The widget displays a read-only preview of the selected file name or preset,
    and provides a button to open a menu with options for importing or clearing
    data. It supports drag-and-drop of `.csv` files, and emits signals when the
    selected value changes or is cleared.

    Signals
    -------
    valueChanged : Signal(str)
        Emitted when a new spectral data source is selected.
    valueCleared : Signal()
        Emitted when the current selection is cleared.

    Parameters
    ----------
    columns : list of str
        Expected column names for validating imported CSV data.
    presets : list of tuple(str, str), optional
        A list of predefined spectral data presets, each specified as a tuple of
        (display name, resource path).
    parent : QWidget or None, optional
        The parent widget, by default None.
    """

    valueChanged = Signal(str)
    valueCleared = Signal()

    def __init__(self,
                 columns: list[str],
                 presets: list[tuple[str, str]] | None = None,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.name_: str | None = None
        self.data_: np.ndarray | None = None

        self._columns = columns
        self._presets = presets

        self._preview = QLineEdit()
        self._preview.setReadOnly(True)
        self._preview.setAcceptDrops(True)
        self._preview.installEventFilter(self)
        self._preview.setPlaceholderText("Select...")

        self._options = QPushButton("...")
        self._options.clicked.connect(self._show_menu)
        self._options.setFixedWidth(30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._preview)
        layout.addWidget(self._options)

    def clear(self):
        """Clears the currently selected spectral data and resets the widget."""
        self.name_ = None
        self.data_ = None
        self._preview.clear()
        self._preview.setPlaceholderText("Select...")
        self.valueCleared.emit()

    def _show_menu(self):
        menu = QMenu(self)
        for name, resource in self._presets:
            menu.addAction(f"Preset: {name}", lambda _name=name, _resource=resource: \
                self._use_preset(_name, _resource))

        menu.addAction("Custom (CSV)", self._browse)
        menu.addSeparator()
        menu.addAction("Remove", self.clear)
        menu.exec(self._options.mapToGlobal(QPoint(0, self._options.height())))

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select Spectra",
            filter="CSV (*.csv)",
        )
        if path:
            self._use_file(path)

    def _use_preset(self, name: str, resource: str):
        resource = QResource(resource)
        with BytesIO(cast(bytes, resource.data())) as file:
            data = np.genfromtxt(file, delimiter=",", names=True)

        self.name_ = name
        self.data_ = data
        self._preview.setText(name)
        self.valueChanged.emit(name)

    def _use_file(self, path: str):
        try:
            data = np.genfromtxt(path, delimiter=",", names=True)
            for name in data.dtype.names:
                if np.isnan(data[name]).any():
                    raise ValueError(f"Column '{name}' contains non-numeric or missing values.")
        except ValueError:
            self._show_invalid_data_error()
            return

        actual = set(data.dtype.names)
        expect = set(self._columns)
        if not actual.issubset(expect):
            self._show_invalid_columns_error()
            return

        self.name_ = path
        self.data_ = data
        self._preview.setText(os.path.basename(path))
        self.valueChanged.emit(path)

    def _show_invalid_data_error(self):
        QMessageBox.critical(
            self,
            "Invalid Data",
            "Could not use the selected file. Please, ensure that it contains only numeric "
            "data, has a header with column names, and that there are no missing values."
        )

    def _show_invalid_columns_error(self):
        QMessageBox.critical(
            self,
            "Invalid Columns",
            f"Could not use the selected file. Please, ensure that it contains columns with "
            f"the following names: {', '.join(self._columns)}."
        )

    def eventFilter(self, watched: QObject, event: QEvent):
        if watched == self._preview:
            if event.type() == QEvent.Type.DragEnter:
                return self._handle_drag_enter(cast(QDragEnterEvent, event))
            if event.type() == QEvent.Type.Drop:
                return self._handle_drop_event(cast(QDropEvent, event))

        return super().eventFilter(watched, event)

    @staticmethod
    def _handle_drag_enter(event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if path.lower().endswith(".csv"):
                event.accept()
        return True

    def _handle_drop_event(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            self._use_file(path)
        return True
