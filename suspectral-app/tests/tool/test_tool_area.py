from unittest.mock import MagicMock

import numpy as np
import pytest
from PySide6.QtCore import QPointF, QRect, Qt, QEvent, QPoint
from PySide6.QtGui import QMouseEvent

from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.tool_area import AreaTool, AreaHighlight
from suspectral.view.image.image_view import ImageView


@pytest.fixture
def mock_view():
    mock = MagicMock(spec=ImageView)
    mock.image.pixmap.return_value.width.return_value = 100
    mock.image.pixmap.return_value.height.return_value = 100
    mock.mapToScene.side_effect = lambda p: QPointF(p.x(), p.y())
    mock.image.mapFromScene.side_effect = lambda p: QPoint(int(p.x()), int(p.y()))
    mock.image.mapRectToScene.side_effect = lambda r: r
    mock.scene.return_value = MagicMock()
    mock.contextMenuRequested = MagicMock()
    mock.viewport.return_value = MagicMock()
    mock.setCursor = MagicMock()
    mock.unsetCursor = MagicMock()
    return mock


@pytest.fixture
def mock_container():
    container = MagicMock(spec=HypercubeContainer)
    container.hypercube.name = "test_cube"
    container.hypercube.wavelengths = np.array([1, 2, 3])
    container.hypercube.read_subregion.return_value = np.ones((2, 2, 3))
    container.hypercube.read_pixels.return_value = np.ones((9, 3))
    return container


@pytest.fixture
def mock_exporter():
    exporter = MagicMock(spec=Exporter)
    exporter.label = "Exporter1"
    exporter.export = MagicMock()
    return exporter


@pytest.fixture
def real_view(qtbot):
    view = ImageView()
    qtbot.addWidget(view)
    return view


@pytest.fixture
def victim(real_view, mock_container, mock_exporter, qtbot):
    tool = AreaTool(real_view, mock_container, [mock_exporter])
    qtbot.addWidget(real_view)
    return tool


def test_deactivate_disconnects_resets(victim, mock_view, qtbot):
    victim.activate()
    with qtbot.waitSignal(victim.selectionEnded):
        victim.deactivate()
    assert victim._selecting is False
    assert victim._highlight is None
    assert victim._samples == []


def make_event(event_type):
    event = MagicMock()
    event.type.return_value = event_type
    return event


def test_event_filter_calls_correct_handlers(victim):
    victim._handle_enter = MagicMock(return_value=True)
    victim._handle_leave = MagicMock(return_value=True)
    victim._handle_mouse_press = MagicMock(return_value=True)
    victim._handle_mouse_move = MagicMock(return_value=True)
    victim._handle_mouse_release = MagicMock(return_value=True)

    victim.eventFilter(None, make_event(QEvent.Type.Enter))
    victim._handle_enter.assert_called_once()

    victim.eventFilter(None, make_event(QEvent.Type.Leave))
    victim._handle_leave.assert_called_once()

    victim.eventFilter(None, make_event(QEvent.Type.MouseButtonPress))
    victim._handle_mouse_press.assert_called_once()

    victim.eventFilter(None, make_event(QEvent.Type.MouseMove))
    victim._handle_mouse_move.assert_called_once()

    victim.eventFilter(None, make_event(QEvent.Type.MouseButtonRelease))
    victim._handle_mouse_release.assert_called_once()


def create_mouse_event(x=10, y=10, button=Qt.MouseButton.LeftButton):
    pos = QPointF(x, y)
    event = MagicMock(spec=QMouseEvent)
    event.button.return_value = button
    event.position.return_value = pos
    return event


def test_handle_enter_calls_set_cursor(victim, mock_view):
    victim._view = mock_view

    result = victim._handle_enter(None)
    assert result is False
    mock_view.setCursor.assert_called_once_with(Qt.CursorShape.CrossCursor)


def test_handle_leave_calls_unset_cursor(victim, mock_view):
    victim._view = mock_view

    result = victim._handle_leave(None)
    assert result is False
    mock_view.unsetCursor.assert_called_once()


def test_start_selection_emits_signal(victim, qtbot):
    event = create_mouse_event()
    with qtbot.waitSignal(victim.selectionStarted):
        victim._handle_mouse_press(event)
    assert victim._selecting is True
    assert victim._samples == []


def test_move_selection_updates_rectangle(victim, qtbot):
    victim._selecting = True
    event = create_mouse_event(20, 20)
    with qtbot.waitSignal(victim.selectionMoved):
        victim._handle_mouse_move(event)
    assert victim._selection_moved is True
    assert isinstance(victim._selection_rect, QRect)


def test_stop_selection_emits_correct_signal(victim, qtbot):
    victim._selecting = True
    victim._selection_moved = True
    victim._selection_source = QPoint(5, 5)
    event = create_mouse_event(15, 15)

    with qtbot.waitSignal(victim.selectionStopped):
        victim._handle_mouse_release(event)

    assert victim._selecting is False
    assert victim._selection_moved is False
    assert isinstance(victim._selection_rect, QRect)
    assert len(victim._samples) > 0


def test_stop_selection_without_movement(victim, qtbot):
    victim._selecting = True
    victim._selection_moved = False
    victim._selection_source = QPoint(5, 5)
    event = create_mouse_event(5, 5)

    with qtbot.waitSignal(victim.selectionEnded):
        victim._handle_mouse_release(event)

    assert victim._selecting is False
    assert victim._selection_rect is None
    assert victim._samples == []


def test_sampling_selection_creates_samples_and_emits(victim, qtbot):
    rect = QRect(QPoint(0, 0), QPoint(10, 10))
    victim._selection_rect = rect

    with qtbot.waitSignal(victim.selectionSampled):
        victim._sample_selection()

    assert isinstance(victim._sample_xs, np.ndarray)
    assert isinstance(victim._sample_ys, np.ndarray)
    assert len(victim._samples) == 9  # 3x3 grid


def test_update_highlight_creates_and_sets_rect(victim, mock_view):
    rect = QRect(QPoint(0, 0), QPoint(10, 10))
    victim._update_highlight(rect)
    assert isinstance(victim._highlight, AreaHighlight)
    assert victim._highlight.rect().width() > 0


def test_get_selection_rect_correct(victim):
    victim._selection_source = QPoint(5, 10)
    victim._selection_target = QPoint(10, 5)
    rect = victim._get_selection_rect()
    assert rect.topLeft() == QPoint(5, 5)
    assert rect.bottomRight() == QPoint(10 + 1, 10 + 1)


def test_get_center_point_clamps_to_image_bounds(victim, mock_view):
    class DummyEvent:
        def position(self):
            return QPointF(-10, 200)

    event = DummyEvent()
    point = victim._get_center_point(event)
    assert 0.0 <= point.x() <= 99.5
    assert 0.0 <= point.y() <= 99.5


def test_export_selection_area_calls_exporter(victim, mock_exporter, mock_container):
    victim._selection_rect = QRect(QPoint(0, 0), QPoint(1, 1))
    victim._container = mock_container

    victim._export_selection_area(mock_exporter)

    assert mock_exporter.export.call_count == 1

    call_args = mock_exporter.export.call_args
    args, kwargs = call_args

    assert args[0] == "test_cube"

    np.testing.assert_array_equal(
        args[1],
        np.ones((4, 3)).reshape(-1, 3)
    )
    np.testing.assert_array_equal(
        args[2],
        mock_container.hypercube.wavelengths
    )


def test_export_selection_points_calls_exporter(victim, mock_exporter, mock_container):
    victim._sample_xs = np.array([0, 1])
    victim._sample_ys = np.array([0, 1])
    victim._container = mock_container

    victim._export_selection_points(mock_exporter)
    assert mock_container.hypercube.read_pixels.call_count == 1
    assert mock_exporter.export.call_count == 1

    call_args = mock_exporter.export.call_args
    args, kwargs = call_args

    assert args[0] == "test_cube"

    np.testing.assert_array_equal(
        args[1],
        np.ones((9, 3))
    )
    np.testing.assert_array_equal(
        args[2],
        mock_container.hypercube.wavelengths
    )


def test_handle_context_menu_adds_actions(victim, mock_exporter):
    menu = MagicMock()
    victim._selection_rect = QRect(QPoint(0, 0), QPoint(1, 1))
    victim._exporters = [mock_exporter]

    victim._handle_context_menu(menu)

    assert menu.addMenu.call_count == 2
    assert menu.addMenu.return_value.addAction.call_count == 2
