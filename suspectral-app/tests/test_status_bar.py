from unittest.mock import Mock

import numpy as np
import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QPixmap

import resources_rc
assert resources_rc

from suspectral.status.status_bar import (
    CursorStatus,
    MemoryStatus,
    ShapeStatus,
    StatusBar,
    StatusBarItem,
    WavelengthStatus,
)

@pytest.fixture
def hypercube():
    mock = Mock()
    mock.num_cols = 100
    mock.num_rows = 200
    mock.num_bands = 150
    mock.num_bytes = 100 * 200 * 150 * 2
    mock.wavelengths = np.arange(400, 700 + 1, 10)
    mock.wavelengths_unit = "nm"
    return mock


def test_status_bar_item_initialization(qtbot):
    victim = StatusBarItem(QPixmap(16, 16))
    qtbot.addWidget(victim)

    assert victim.layout().count() == 2
    assert victim._label.text() == ""


def test_status_bar_item_clear(qtbot):
    victim = StatusBarItem(QPixmap(16, 16))
    qtbot.addWidget(victim)

    victim._label.setText("Lorem ipsum")
    assert victim._label.text() != ""

    victim.clear()
    assert victim._label.text() == ""


def test_cursor_status_initialization(qtbot):
    victim = CursorStatus()
    qtbot.addWidget(victim)

    assert not victim._icon.pixmap().isNull()
    assert not victim._label.text()


def test_cursor_status_set_position(qtbot):
    victim = CursorStatus()
    qtbot.addWidget(victim)

    position = QPoint(42, 88)
    victim.set(position)
    assert victim._label.text() == "42, 88px"


def test_cursor_status_set_none(qtbot):
    victim = CursorStatus()
    qtbot.addWidget(victim)

    victim.set(QPoint(5, 10))
    victim.set(None)
    assert victim._label.text() == ""


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


def test_memory_status_set_value(qtbot):
    victim = MemoryStatus()
    qtbot.addWidget(victim)

    victim.set(2048)
    assert victim._label.text() == "2.00 KB"


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
def test_memory_status_stringify(num_bytes, expected):
    assert MemoryStatus._stringify(num_bytes) == expected


def test_memory_status_set_negative_value(qtbot):
    victim = MemoryStatus()
    qtbot.addWidget(victim)

    with pytest.raises(AssertionError):
        victim.set(-1234)


def test_wavelength_status_initialization(qtbot):
    victim = WavelengthStatus()
    qtbot.addWidget(victim)

    assert not victim._icon.pixmap().isNull()
    assert victim._label.text() == ""


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


def test_wavelength_status_single_value(qtbot):
    victim = WavelengthStatus()
    qtbot.addWidget(victim)

    with pytest.raises(AssertionError):
        victim.set(np.array([555.0]))


def test_wavelength_status_empty_array(qtbot):
    victim = WavelengthStatus()
    qtbot.addWidget(victim)

    with pytest.raises(AssertionError):
        victim.set(np.array([]), "nm")


def test_status_bar_initialization(qtbot):
    victim = StatusBar()
    qtbot.addWidget(victim)

    assert victim._shape_status._label.text() == ""
    assert victim._cursor_status._label.text() == ""
    assert victim._memory_status._label.text() == ""
    assert victim._wavelength_status._label.text() == ""


def test_status_bar_update_hypercube_status(qtbot, hypercube):
    victim = StatusBar()
    qtbot.addWidget(victim)

    victim.update_hypercube_status(hypercube)

    assert victim._shape_status._label.text() == "100 × 200 × 150"
    assert victim._wavelength_status._label.text() == "400 : 700 : 10 (nm)"
    assert victim._memory_status._label.text() == "5.72 MB"


def test_status_bar_update_cursor_status(qtbot):
    victim = StatusBar()
    qtbot.addWidget(victim)

    victim.update_cursor_status(QPoint(10, 20))
    assert victim._cursor_status._label.text() == "10, 20px"


def test_status_bar_clear(qtbot):
    victim = StatusBar()
    qtbot.addWidget(victim)

    victim._shape_status._label.setText("dummy")
    victim._cursor_status._label.setText("dummy")
    victim._memory_status._label.setText("dummy")
    victim._wavelength_status._label.setText("dummy")

    victim.clear()

    assert victim._shape_status._label.text() == ""
    assert victim._cursor_status._label.text() == ""
    assert victim._memory_status._label.text() == ""
    assert victim._wavelength_status._label.text() == ""
