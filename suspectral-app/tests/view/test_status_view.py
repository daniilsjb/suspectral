from unittest.mock import MagicMock

import numpy as np
import pytest
from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPixmap

from suspectral.view.status.status_view import StatusView
from suspectral.view.status.status_cursor import CursorStatus
from suspectral.view.status.status_memory import MemoryStatus
from suspectral.view.status.status_shape import ShapeStatus
from suspectral.view.status.status_view_item import StatusViewItem
from suspectral.view.status.status_wavelength import WavelengthStatus

import resources
assert resources


@pytest.fixture
def hypercube():
    mock = MagicMock()
    mock.num_cols = 100
    mock.num_rows = 200
    mock.num_bands = 150
    mock.num_bytes = 100 * 200 * 150 * 2
    mock.wavelengths = np.arange(400, 700 + 1, 10)
    mock.wavelengths_unit = "nm"
    return mock


def test_status_view_item_clear(qtbot):
    victim = StatusViewItem(QPixmap(16, 16))
    qtbot.addWidget(victim)

    victim._label.setText("Lorem ipsum")
    assert victim._label.text()

    victim.clear()
    assert not victim._label.text()


def test_cursor_status_initialization(qtbot):
    victim = CursorStatus()
    qtbot.addWidget(victim)

    assert not victim._icon.pixmap().isNull()
    assert not victim._label.text()


def test_cursor_status_set_position(qtbot):
    victim = CursorStatus()
    qtbot.addWidget(victim)

    victim.set(QPoint(42, 88))
    assert victim._label.text() == "42, 88px"


def test_shape_status_initialization(qtbot):
    victim = ShapeStatus()
    qtbot.addWidget(victim)

    assert not victim._icon.pixmap().isNull()
    assert not victim._label.text()


def test_shape_status_set_values(qtbot):
    victim = ShapeStatus()
    qtbot.addWidget(victim)

    victim.set(num_cols=128, num_rows=256, num_bands=31)
    assert victim._label.text() == "128 × 256 × 31"


def test_memory_status_initialization(qtbot):
    victim = MemoryStatus()
    qtbot.addWidget(victim)

    assert not victim._icon.pixmap().isNull()
    assert not victim._label.text()


@pytest.mark.parametrize("num_bytes,expected", [
    (0, "0.00 B"),
    (1, "1.00 B"),
    (512, "512.00 B"),
    (1023, "1023.00 B"),
    (1024, "1.00 KB"),
    (1500, "1.46 KB"),
    (1536, "1.50 KB"),
    (1_048_576, "1.00 MB"),
    (1_500_000, "1.43 MB"),
    (1_050_000_000, "1001.36 MB"),
    (1_073_741_824, "1.00 GB"),
    (2_500_000_000, "2.33 GB"),
    (1_099_511_627_776, "1.00 TB"),
    (3_750_000_000_000, "3.41 TB"),
    (1_125_899_906_842_624, "1.00 PB"),
    (5_500_000_000_000_000, "4.88 PB"),
    (1_152_921_504_606_846_976, "1.00 EB"),
])
def test_memory_status_stringify(qtbot, num_bytes, expected):
    victim = MemoryStatus()
    qtbot.addWidget(victim)

    victim.set(num_bytes)
    assert victim._label.text() == expected


def test_memory_status_set_negative_value(qtbot):
    victim = MemoryStatus()
    qtbot.addWidget(victim)

    with pytest.raises(AssertionError):
        victim.set(-1234)


def test_wavelength_status_initialization(qtbot):
    victim = WavelengthStatus()
    qtbot.addWidget(victim)

    assert not victim._icon.pixmap().isNull()
    assert not victim._label.text()


@pytest.mark.parametrize("wavelengths,wavelengths_unit,expected_text", [
    (np.array([400.0, 410.0, 420.0]), "nm", "400 : 420 : 10 (nm)"),
    (np.array([500.123, 505.123, 510.123]), "nm", "500.12 : 510.12 : 5 (nm)"),
    (np.array([1000.0, 1100.0, 1300.0]), "μm", "1000 : 1300 (μm)"),
    (np.array([1.2345, 2.3456]), "eV", "1.23 : 2.35 : 1.11 (eV)"),
    (np.array([700, 710, 720]), None, "700 : 720 : 10"),
    (np.array([700, 705, 715]), None, "700 : 715"),
])
def test_wavelength_status_set(qtbot, wavelengths, wavelengths_unit, expected_text):
    victim = WavelengthStatus()
    qtbot.addWidget(victim)

    victim.set(wavelengths, wavelengths_unit)
    assert victim._label.text() == expected_text


def test_status_view_initialization(qtbot):
    victim = StatusView()
    qtbot.addWidget(victim)

    assert not victim._shape_status._label.text()
    assert not victim._cursor_status._label.text()
    assert not victim._memory_status._label.text()
    assert not victim._wavelength_status._label.text()


def test_status_view_update_hypercube_status(qtbot, hypercube):
    victim = StatusView()
    qtbot.addWidget(victim)

    victim.update_hypercube(hypercube)
    assert victim._shape_status._label.text() == "100 × 200 × 150"
    assert victim._memory_status._label.text() == "5.72 MB"
    assert victim._wavelength_status._label.text() == "400 : 700 : 10 (nm)"


def test_status_view_update_hypercube_status_without_wavelengths(qtbot, hypercube):
    victim = StatusView()
    qtbot.addWidget(victim)

    hypercube.wavelengths = None
    victim.update_hypercube(hypercube)
    assert victim._shape_status._label.text() == "100 × 200 × 150"
    assert victim._memory_status._label.text() == "5.72 MB"
    assert not victim._wavelength_status._label.text()


def test_status_view_update_cursor_status(qtbot):
    victim = StatusView()
    qtbot.addWidget(victim)

    victim.update_cursor(QPoint(10, 20))
    assert victim._cursor_status._label.text() == "10, 20px"
    victim.clear_cursor()
    assert not victim._cursor_status._label.text()


def test_status_view_update_selection_status(qtbot):
    victim = StatusView()
    qtbot.addWidget(victim)

    victim.update_selection(QRect(10, 10, 100, 100))
    assert victim._selection_status._label.text() == "99 × 99px"
    victim.clear_selection()
    assert not victim._selection_status._label.text()


def test_status_view_clear(qtbot):
    victim = StatusView()
    qtbot.addWidget(victim)

    victim._shape_status._label.setText("Lorem ipsum dolor sit amet")
    victim._cursor_status._label.setText("Lorem ipsum dolor sit amet")
    victim._memory_status._label.setText("Lorem ipsum dolor sit amet")
    victim._selection_status._label.setText("Lorem ipsum dolor sit amet")
    victim._wavelength_status._label.setText("Lorem ipsum dolor sit amet")

    victim.clear()

    assert not victim._shape_status._label.text()
    assert not victim._cursor_status._label.text()
    assert not victim._memory_status._label.text()
    assert not victim._selection_status._label.text()
    assert not victim._wavelength_status._label.text()
