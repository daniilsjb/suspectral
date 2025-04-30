import pytest

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

from suspectral.metadata.metadata_view import MetadataView


@pytest.fixture
def victim(qtbot):
    widget = MetadataView()
    qtbot.addWidget(widget)
    return widget


def test_initialization(victim):
    assert victim.autoFillBackground() is True
    assert victim.backgroundRole() == QPalette.ColorRole.Base

    placeholder = victim._placeholder
    assert victim.currentWidget() == victim._placeholder

    assert placeholder.text() == "Load a hypercube to see its metadata."
    assert placeholder.alignment() == (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    table = victim._table
    assert table.rowCount() == 0
    assert table.columnCount() == 2


def test_set_items(victim):
    victim.set_items({
        "Key 1": "Value 1",
        "Key 2": ["1", "2", "3"],
        "Key 3": "123",
        "Key 4": "45.67",
    })

    table = victim._table
    assert table.rowCount() == 4

    assert table.item(0, 0).text() == "Key 1"
    assert table.item(0, 1).text() == "Value 1"
    assert table.item(1, 0).text() == "Key 2"
    assert table.item(1, 1).text() == "{1, 2, 3}"
    assert table.item(2, 0).text() == "Key 3"
    assert table.item(2, 1).text() == "123"
    assert table.item(3, 0).text() == "Key 4"
    assert table.item(3, 1).text() == "45.67"

    assert victim.currentWidget() == victim._table


def test_clear(victim):
    victim.set_items({
        "Key 1": "Value 1",
    })

    table = victim._table
    assert table.rowCount() == 1
    assert table.item(0, 0).text() == "Key 1"
    assert table.item(0, 1).text() == "Value 1"

    victim.clear()

    assert table.rowCount() == 0
    assert victim.currentWidget() == victim._placeholder


@pytest.mark.parametrize("test_input, expected", [("123", 123), ("45.67", 45.67), ("Hello", "Hello"), ("True", "True")])
def test_stringify(test_input, expected):
    result = MetadataView._stringify(test_input)
    assert result == expected
