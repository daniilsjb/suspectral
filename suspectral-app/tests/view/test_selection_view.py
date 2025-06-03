import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QLabel

from suspectral.view.selection.selection_view import SelectionView


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
    assert victim._table.item(0, 1).text() == "10"
    assert victim._table.item(0, 2).text() == "20"


def test_add_multiple_points(victim):
    points = [QPoint(1, 2), QPoint(3, 4), QPoint(5, 6)]
    victim.add_points(points)

    assert victim.currentWidget() == victim._table
    assert victim._table.rowCount() == 3

    for row, point in enumerate(points):
        assert victim._table.item(row, 1).text() == str(point.x())
        assert victim._table.item(row, 2).text() == str(point.y())


def test_clear_resets_table_and_view(victim):
    victim.add_point(QPoint(10, 20))
    victim.clear()

    assert victim.currentWidget() == victim._placeholder
    assert victim._table.rowCount() == 0
