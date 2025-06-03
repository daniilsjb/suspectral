from unittest.mock import MagicMock

import pytest

from suspectral.tool.manager import ToolManager
from suspectral.tool.tool import Tool
from suspectral.view.image.image_view import ImageView
from suspectral.view.toolbar.toolbar_view import ToolbarView


@pytest.fixture
def mock_image_view():
    return MagicMock(spec=ImageView)


@pytest.fixture
def mock_tools():
    tools = MagicMock(spec=ToolManager)
    tools.pan = MagicMock(spec=Tool)
    tools.none = MagicMock(spec=Tool)
    tools.area = MagicMock(spec=Tool)
    tools.zoom = MagicMock(spec=Tool)
    tools.inspect = MagicMock(spec=Tool)
    return tools


@pytest.fixture
def victim(qtbot, mock_image_view, mock_tools):
    widget = ToolbarView(image=mock_image_view, tools=mock_tools)
    qtbot.addWidget(widget)
    return widget


def test_toolbar_initial_state(victim):
    assert victim.toolTip() == "Toolbar"
    assert not victim.isMovable()
    assert not victim.isEnabled()
    assert not victim.isFloatable()


def test_tools_added_to_action_group(victim):
    group = victim._group
    assert group.isExclusive()

    names = [action.text() for action in group.actions()]
    assert set(names) == {"None", "Pan", "Inspect", "Select Area", "Zoom"}


def test_correct_default_tool_checked(victim):
    checked = [a for a in victim._group.actions() if a.isChecked()]
    assert len(checked) == 1
    assert checked[0].text() == "None"


def test_select_tool_triggers_tool_manager(victim, mock_tools):
    action = [a for a in victim._group.actions() if a.text() == "Zoom"][0]
    victim._select_tool(action)
    mock_tools.set.assert_called_once_with(action.data())


def test_image_methods_triggered(mock_image_view, victim, qtbot):
    action_map = {
        "Zoom In": mock_image_view.zoom_in,
        "Zoom Out": mock_image_view.zoom_out,
        "Rotate Left": mock_image_view.rotate_left,
        "Rotate Right": mock_image_view.rotate_right,
        "Flip Vertical": mock_image_view.flip_vertically,
        "Flip Horizontal": mock_image_view.flip_horizontally,
    }

    for name, method in action_map.items():
        action = next(a for a in victim.actions() if a and a.text() == name)
        with qtbot.waitSignal(action.triggered, timeout=500):
            action.trigger()

        method.assert_called_once()
