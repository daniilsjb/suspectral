from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QEvent, Qt, QObject

from suspectral.tool.tool_zoom import ZoomTool
from suspectral.view.image.image_view import ImageView

import resources
assert resources


class DummyEvent(QObject):
    def __init__(self, event_type):
        super().__init__()
        self._type = event_type

    def type(self):
        return self._type


@pytest.fixture
def mock_image_view():
    return MagicMock(spec=ImageView)


@pytest.fixture
def victim(mock_image_view):
    return ZoomTool(view=mock_image_view)


def test_event_filter_enter_sets_cursor(qtbot, victim, mock_image_view):
    event = DummyEvent(QEvent.Type.Enter)
    result = victim.eventFilter(QObject(), event)
    mock_image_view.setCursor.assert_called_once_with(victim._cursor)
    assert result is False


def test_event_filter_leave_unsets_cursor(qtbot, victim, mock_image_view):
    event = DummyEvent(QEvent.Type.Leave)
    result = victim.eventFilter(QObject(), event)
    mock_image_view.unsetCursor.assert_called_once()
    assert result is False


def test_event_filter_context_menu_filtered_out(qtbot, victim):
    event = DummyEvent(QEvent.Type.ContextMenu)
    result = victim.eventFilter(QObject(), event)
    assert result is True


@pytest.mark.parametrize("button,expected_zoom", [
    (Qt.MouseButton.LeftButton, "zoom_in"),
    (Qt.MouseButton.RightButton, "zoom_out"),
    (Qt.MouseButton.MiddleButton, None),
])
def test_mouse_release_handling_integration(qtbot, mocker, button, expected_zoom):
    image_view = ImageView()
    qtbot.addWidget(image_view)

    zoom_in = mocker.patch.object(image_view, "zoom_in")
    zoom_out = mocker.patch.object(image_view, "zoom_out")

    zoom_tool = ZoomTool(image_view)
    zoom_tool.activate()

    image_view.show()
    qtbot.waitExposed(image_view)

    qtbot.mouseClick(image_view.viewport(), button)

    if expected_zoom == "zoom_in":
        zoom_in.assert_called_once_with(2.0)
        zoom_out.assert_not_called()
    elif expected_zoom == "zoom_out":
        zoom_out.assert_called_once_with(2.0)
        zoom_in.assert_not_called()
    else:
        zoom_in.assert_not_called()
        zoom_out.assert_not_called()


def test_deactivate_calls_unset_cursor_and_super(qtbot, victim, mock_image_view, mocker):
    super_deactivate = mocker.patch("suspectral.tool.tool_zoom.Tool.deactivate")
    victim.deactivate()
    mock_image_view.unsetCursor.assert_called_once()
    super_deactivate.assert_called_once()


def test_event_filter_falls_back_to_super_for_other_events(qtbot, victim, mock_image_view, mocker):
    unknown_event = DummyEvent(QEvent.Type.KeyPress)
    super_filter = mocker.patch("suspectral.tool.tool_zoom.Tool.eventFilter", return_value=True)
    result = victim.eventFilter(QObject(), unknown_event)
    super_filter.assert_called_once()
    assert result is True
