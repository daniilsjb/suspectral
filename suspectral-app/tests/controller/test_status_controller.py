from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QPoint, QRect, QObject, Signal

from suspectral.controller.status_controller import StatusController
from suspectral.model.hypercube import Hypercube
from suspectral.tool.manager import ToolManager
from suspectral.view.image.image_view import ImageView
from suspectral.view.status_view import StatusView


class DummyHypercube(QObject):
    opened = Signal(Hypercube)
    closed = Signal()


@pytest.fixture
def victim(qtbot):
    return StatusController(
        view=MagicMock(StatusView),
        image=MagicMock(ImageView),
        tools=MagicMock(ToolManager),
        model=DummyHypercube(),
    )


def test_handle_hypercube_opened(victim, qtbot):
    hypercube = MagicMock(Hypercube)
    victim._handle_hypercube_opened(hypercube)
    victim._view.update_hypercube.assert_called_once_with(hypercube)


def test_handle_hypercube_closed(victim, qtbot):
    victim._handle_hypercube_closed()
    victim._view.clear.assert_called_once()


def test_handle_selection_moved(victim, qtbot):
    selection = QRect(0, 0, 10, 10)
    victim._handle_selection_moved(selection)
    victim._view.update_selection.assert_called_once_with(selection)


def test_handle_selection_ended(victim, qtbot):
    victim._handle_selection_ended()
    victim._view.clear_selection.assert_called_once()


def test_handle_cursor_inside(victim, qtbot):
    point = QPoint(5, 5)
    victim._handle_cursor_inside(point)
    victim._view.update_cursor.assert_called_once_with(point)


def test_handle_cursor_outside(victim, qtbot):
    victim._handle_cursor_outside()
    victim._view.clear_cursor.assert_called_once()


def test_hypercube_opened_signal(victim, qtbot):
    hypercube = MagicMock(Hypercube)
    victim._model.opened.emit(hypercube)
    victim._view.update_hypercube.assert_called_once_with(hypercube)


def test_hypercube_closed_signal(victim, qtbot):
    victim._model.closed.emit()
    victim._view.clear.assert_called_once()


def test_hypercube_opened_boundary(victim, qtbot):
    boundary_hypercube = MagicMock(Hypercube)
    victim._handle_hypercube_opened(boundary_hypercube)
    victim._view.update_hypercube.assert_called_once_with(boundary_hypercube)


def test_selection_moved_boundary(victim, qtbot):
    boundary_selection = QRect(0, 0, 0, 0)
    victim._handle_selection_moved(boundary_selection)
    victim._view.update_selection.assert_called_once_with(boundary_selection)


def test_cursor_inside_boundary(victim, qtbot):
    boundary_point = QPoint(0, 0)
    victim._handle_cursor_inside(boundary_point)
    victim._view.update_cursor.assert_called_once_with(boundary_point)


def test_cursor_outside_boundary(victim, qtbot):
    victim._handle_cursor_outside()
    victim._view.clear_cursor.assert_called_once()
