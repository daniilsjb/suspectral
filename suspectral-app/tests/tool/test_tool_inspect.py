from unittest.mock import create_autospec, MagicMock

import pytest
from PySide6.QtCore import Qt, QPoint, QEvent, QPointF
from PySide6.QtGui import QMouseEvent, QAction, QPixmap, QColor
from PySide6.QtWidgets import QMenu, QGraphicsScene

from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.tool_inspect import InspectTool


@pytest.fixture
def image_view(qtbot):
    from suspectral.view.image.image_view import ImageView
    view = ImageView()
    qtbot.addWidget(view)
    view.display(QPixmap(10, 10))
    return view


@pytest.fixture
def container():
    mock = create_autospec(HypercubeContainer)
    mock.hypercube.name = "cube"
    mock.hypercube.read_pixels.return_value = [[1, 2, 3]]
    mock.hypercube.bands = [400, 500, 600]
    return mock


@pytest.fixture
def exporter():
    mock = create_autospec(Exporter)
    mock.label = "CSV"
    return mock


@pytest.fixture
def victim(image_view, container, exporter):
    return InspectTool(image_view, container, [exporter])


def test_activate_installs_event_filter_and_connects_signal(qtbot, victim):
    victim._handle_context_menu = MagicMock()
    victim.activate()
    victim._view.contextMenuRequested.emit(QMenu())
    victim._handle_context_menu.assert_called_once()


def test_deactivate_removes_event_filter_and_disconnects_signal(qtbot, victim):
    victim.activate()
    victim._remove_highlight = MagicMock()
    victim._remove_crosshair = MagicMock()
    view = victim._view
    victim.deactivate()
    view.contextMenuRequested.emit(QMenu())
    victim._remove_highlight.assert_called_once()
    victim._remove_crosshair.assert_called_once()


@pytest.mark.parametrize("event_type,handler", [
    (QEvent.Type.Enter, '_handle_enter'),
    (QEvent.Type.Leave, '_handle_leave'),
    (QEvent.Type.MouseMove, '_handle_mouse_move'),
    (QEvent.Type.MouseButtonRelease, '_handle_mouse_release'),
])
def test_event_filter_dispatch(qtbot, victim, event_type, handler):
    event = create_autospec(QEvent, instance=True)
    event.type.return_value = event_type
    setattr(victim, handler, MagicMock(return_value=False))
    victim.eventFilter(object(), event)
    getattr(victim, handler).assert_called_once()


def test_handle_enter_sets_cursor(victim):
    victim._view.setCursor = MagicMock()
    result = victim._handle_enter(QEvent(QEvent.Type.Enter))
    victim._view.setCursor.assert_called_once()
    assert result is False


def test_handle_leave_unsets_cursor(victim):
    victim._view.unsetCursor = MagicMock()
    result = victim._handle_leave(QEvent(QEvent.Type.Leave))
    victim._view.unsetCursor.assert_called_once()
    assert result is False


def test_handle_mouse_release_left_button_triggers_inspect(qtbot, victim):
    event = create_autospec(QMouseEvent)
    event.button.return_value = Qt.MouseButton.LeftButton
    victim._inspect = MagicMock()
    victim._handle_mouse_release(event)
    victim._inspect.assert_called_once()


def test_handle_mouse_release_other_button_does_nothing(qtbot, victim):
    event = create_autospec(QMouseEvent)
    event.button.return_value = Qt.MouseButton.RightButton
    victim._inspect = MagicMock()
    victim._handle_mouse_release(event)
    victim._inspect.assert_not_called()


def test_inspect_outside_clears_points_and_emits_clear(qtbot, victim):
    view = victim._view
    victim._points = [QPoint(1, 1)]
    victim._remove_crosshair = MagicMock()

    cleared_mock = MagicMock()
    victim.pixelCleared.connect(cleared_mock)

    view.image.setPixmap(QPixmap(10, 10))

    event = QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        QPointF(-1, -1),
        QPointF(-1, -1),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    event.position = lambda: QPointF(-1, -1)

    victim._inspect(event)

    cleared_mock.assert_called_once()
    assert victim._points == []
    victim._remove_crosshair.assert_called_once()


def test_handle_context_menu_adds_export_actions(qtbot, victim, exporter):
    menu = QMenu()
    victim._points.append(QPoint(0, 0))
    victim._handle_context_menu(menu)
    assert any(isinstance(a, QAction) and "Export to" in a.text() for a in menu.actions())


def test_export_selection_calls_exporter(victim, exporter):
    victim._points = [QPoint(1, 2)]
    victim._export_selection(exporter)
    exporter.export.assert_called_once()


def test_update_highlight_creates_and_sets_rect(victim):
    scene = MagicMock(spec=QGraphicsScene)
    victim._view.scene = lambda: scene
    victim._highlight = None
    victim._update_highlight(QPoint(5, 5))
    assert victim._highlight is not None


def test_remove_highlight_removes_and_nulls(victim):
    scene = MagicMock(spec=QGraphicsScene)
    victim._view.scene = lambda: scene
    victim._highlight = MagicMock()
    victim._remove_highlight()
    scene.removeItem.assert_called_once()
    assert victim._highlight is None


def test_append_crosshair_adds_to_scene(victim):
    scene = MagicMock(spec=QGraphicsScene)
    victim._view.scene = lambda: scene
    color = QColor(255, 0, 0)
    victim._append_crosshair(QPoint(0, 0), color)
    assert len(victim._crosshair) == 1
    scene.addItem.assert_called_once()


def test_remove_crosshair_clears_scene(victim):
    item = MagicMock()
    victim._crosshair = [item]
    scene = MagicMock(spec=QGraphicsScene)
    victim._view.scene = lambda: scene
    victim._remove_crosshair()
    scene.removeItem.assert_called_once_with(item)
    assert victim._crosshair == []
