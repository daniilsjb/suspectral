import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QLabel

from suspectral.selection.selection_view import SelectionView


@pytest.fixture
def victim(qtbot):
    widget = SelectionView()
    qtbot.addWidget(widget)
    return widget


def test_initialization(victim):
    assert victim.currentWidget() == victim._placeholder
    assert isinstance(victim._placeholder, QLabel)
    assert victim._table.rowCount() == 0


def test_add_single_point(victim):
    point = QPoint(10, 20)
    victim.add_point(point)

    assert victim.currentWidget() == victim._table
    assert victim._table.rowCount() == 1

    x_item = victim._table.item(0, 1)
    y_item = victim._table.item(0, 2)

    assert x_item.text() == "10"
    assert y_item.text() == "20"
    assert x_item.textAlignment() == Qt.AlignmentFlag.AlignCenter
    assert y_item.textAlignment() == Qt.AlignmentFlag.AlignCenter


def test_add_multiple_points(victim):
    points = [QPoint(1, 2), QPoint(3, 4), QPoint(5, 6)]
    victim.add_points(points)

    assert victim.currentWidget() == victim._table
    assert victim._table.rowCount() == 3

    for row, point in enumerate(points):
        x_item = victim._table.item(row, 1)
        y_item = victim._table.item(row, 2)
        assert x_item.text() == str(point.x())
        assert y_item.text() == str(point.y())
        assert x_item.textAlignment() == Qt.AlignmentFlag.AlignCenter
        assert y_item.textAlignment() == Qt.AlignmentFlag.AlignCenter


def test_clear_resets_table_and_view(victim):
    victim.add_point(QPoint(10, 20))
    victim.clear()

    assert victim.currentWidget() == victim._placeholder
    assert victim._table.rowCount() == 0
    for row in range(victim._table.rowCount()):
        for col in range(3):
            assert victim._table.item(row, col) is None


def test_color_cell_not_editable_or_selectable(victim):
    victim.add_point(QPoint(1, 1))
    item = victim._table.item(0, 0)

    assert not item.flags() & Qt.ItemFlag.ItemIsSelectable
    assert not item.flags() & Qt.ItemFlag.ItemIsEditable
