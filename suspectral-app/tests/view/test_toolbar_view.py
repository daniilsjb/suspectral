from unittest.mock import Mock

import pytest
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QApplication

from suspectral.tool.manager import ToolManager
from suspectral.tool.tool import Tool
from suspectral.view.image.image_view import ImageView
from suspectral.view.toolbar_view import ToolbarView


class DummyModel(QObject):
    opened = Signal()
    closed = Signal()


@pytest.fixture
def mock_image():
    return Mock(spec=ImageView)


@pytest.fixture
def mock_model():
    return DummyModel()


@pytest.fixture
def mock_tools():
    tools = Mock(spec=ToolManager)
    tools.none = Mock(spec=Tool)
    tools.drag = Mock(spec=Tool)
    tools.inspect = Mock(spec=Tool)
    tools.area = Mock(spec=Tool)
    tools.zoom = Mock(spec=Tool)
    return tools


@pytest.fixture
def toolbar_view(qtbot, mock_image, mock_tools, mock_model):
    widget = ToolbarView(image=mock_image, tools=mock_tools, model=mock_model)
    qtbot.addWidget(widget)
    return widget


def test_toolbar_initial_state(toolbar_view):
    assert toolbar_view.toolTip() == "Toolbar"
    assert toolbar_view.iconSize().width() == 20
    assert not toolbar_view.isMovable()
    assert not toolbar_view.isFloatable()
    assert not toolbar_view.isEnabled()


def test_model_signals_enable_toolbar(toolbar_view, mock_model):
    assert not toolbar_view.isEnabled()
    mock_model.opened.emit()
    assert toolbar_view.isEnabled()
    mock_model.closed.emit()
    assert not toolbar_view.isEnabled()


def test_tools_added_to_action_group(toolbar_view):
    group = toolbar_view._action_group
    actions = group.actions()
    names = [action.text() for action in actions]
    expected = {"None", "Drag", "Inspect", "Select Area", "Zoom"}
    assert set(names) == expected
    assert group.isExclusive()


def test_correct_default_tool_checked(toolbar_view):
    checked = [a for a in toolbar_view._action_group.actions() if a.isChecked()]
    assert len(checked) == 1
    assert checked[0].text() == "None"


def test_select_tool_triggers_tool_manager(toolbar_view, mock_tools):
    action = [a for a in toolbar_view._action_group.actions() if a.text() == "Zoom"][0]
    toolbar_view._select_tool(action)
    mock_tools.set.assert_called_once_with(action.data())


def test_all_toolbar_actions_present(toolbar_view):
    action_names = [action.text() for action in toolbar_view.actions()]
    expected = {
        "None", "Drag", "Inspect", "Select Area", "Zoom",
        "",
        "Rotate Left", "Rotate Right", "Flip Horizontal", "Flip Vertical", "Zoom In", "Zoom Out",
    }
    assert set(action_names) == expected


def test_image_methods_triggered(mock_image, toolbar_view, qtbot):
    action_map = {
        "Rotate Left": mock_image.rotate_left,
        "Rotate Right": mock_image.rotate_right,
        "Flip Horizontal": mock_image.flip_horizontally,
        "Flip Vertical": mock_image.flip_vertically,
        "Zoom In": mock_image.zoom_in,
        "Zoom Out": mock_image.zoom_out,
    }

    for name, method in action_map.items():
        method.reset_mock()
        action = next(a for a in toolbar_view.actions() if a and a.text() == name)
        with qtbot.waitSignal(action.triggered, timeout=100):
            action.trigger()
        method.assert_called_once()


def test_highlight_color(monkeypatch):
    class DummyStyleHints:
        def colorScheme(self):
            return Qt.ColorScheme.Dark

    monkeypatch.setattr(QApplication, "styleHints", lambda: DummyStyleHints())
    assert ToolbarView._highlight_color() == "#3b82f6"

    DummyStyleHints.colorScheme = lambda self: Qt.ColorScheme.Light
    monkeypatch.setattr(QApplication, "styleHints", lambda: DummyStyleHints())
    assert ToolbarView._highlight_color() == "#bfdbfe"
