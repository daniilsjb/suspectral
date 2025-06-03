from unittest.mock import MagicMock

import numpy as np
import pytest
from PySide6.QtCore import QPoint

from suspectral.controller.selection_controller import SelectionController
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.manager import ToolManager
from suspectral.view.selection.selection_view import SelectionView


@pytest.fixture
def victim(qtbot):
    return SelectionController(
        tools=MagicMock(spec=ToolManager),
        model=MagicMock(spec=HypercubeContainer),
        view=MagicMock(spec=SelectionView),
    )


def test_handle_hypercube_opened(victim, qtbot):
    victim._handle_hypercube_opened()
    victim._view.clear.assert_called_once()


def test_handle_hypercube_closed(victim, qtbot):
    victim._handle_hypercube_closed()
    victim._view.clear.assert_called_once()


def test_handle_tool_changed(victim, qtbot):
    victim._handle_tool_changed()
    victim._view.clear.assert_called_once()


def test_handle_selection_changed(victim, qtbot):
    victim._handle_selection_changed()
    victim._view.clear.assert_called_once()


def test_handle_selection_sampled(victim, qtbot):
    xs = np.array([1, 2])
    ys = np.array([3, 4])
    victim._handle_selection_sampled(xs, ys)
    victim._view.add_points.assert_called_once_with([
        QPoint(1, 3),
        QPoint(2, 3),
        QPoint(1, 4),
        QPoint(2, 4),
    ])


def test_handle_pixel_clicked(victim, qtbot):
    point = QPoint(10, 20)
    victim._handle_pixel_clicked(point)
    victim._view.add_point.assert_called_once_with(point)


def test_handle_pixel_cleared(victim, qtbot):
    victim._handle_pixel_cleared()
    victim._view.clear.assert_called_once()


def test_boundary_value_for_selection_sampled(victim, qtbot):
    xs = np.array([0])
    ys = np.array([0])
    victim._handle_selection_sampled(xs, ys)
    victim._view.add_points.assert_called_once_with([QPoint(0, 0)])


def test_empty_selection_sampled(victim, qtbot):
    xs = np.array([])
    ys = np.array([])
    victim._handle_selection_sampled(xs, ys)
    victim._view.add_points.assert_called_once_with([])


@pytest.mark.parametrize("point", [
    QPoint(10, 10), QPoint(-1, -1), QPoint(0, 0)
])
def test_handle_pixel_cleared_multiple(victim, qtbot, point):
    victim._handle_pixel_clicked(point)
    victim._handle_pixel_cleared()
    victim._view.clear.assert_called_once()
