from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QObject, Signal

from suspectral.exporter.exporter import Exporter
from suspectral.tool.manager import ToolManager
from suspectral.tool.tool_area import AreaTool
from suspectral.tool.tool_pan import PanTool
from suspectral.tool.tool_inspect import InspectTool
from suspectral.tool.tool_none import NoneTool
from suspectral.tool.tool_zoom import ZoomTool
from suspectral.view.image.image_view import ImageView


class DummyModel(QObject):
    opened = Signal()
    closed = Signal()


@pytest.fixture
def mock_model():
    return DummyModel()


@pytest.fixture
def mock_view():
    return MagicMock(spec=ImageView)


@pytest.fixture
def mock_exporters():
    return [MagicMock(spec=Exporter)]


@pytest.fixture
def victim(mock_view, mock_model, mock_exporters):
    return ToolManager(view=mock_view, model=mock_model, exporters=mock_exporters)


def test_tool_manager_initialization(qtbot, victim):
    assert isinstance(victim.none, NoneTool)
    assert isinstance(victim.pan, PanTool)
    assert isinstance(victim.zoom, ZoomTool)
    assert isinstance(victim.area, AreaTool)
    assert isinstance(victim.inspect, InspectTool)
    assert victim._active_tool == victim.none


def test_set_tool_switching(qtbot, victim):
    mock_none_activate = MagicMock()
    mock_none_deactivate = MagicMock()
    mock_drag_activate = MagicMock()
    mock_drag_deactivate = MagicMock()

    victim.none.activate = mock_none_activate
    victim.none.deactivate = mock_none_deactivate
    victim.pan.activate = mock_drag_activate
    victim.pan.deactivate = mock_drag_deactivate

    victim.set(victim.pan)
    assert victim._active_tool == victim.pan

    mock_none_deactivate.assert_called_once()
    mock_drag_activate.assert_called_once()


def test_tool_changed_signal_emission(qtbot, victim):
    mock_signal_listener = MagicMock()
    victim.toolChanged.connect(mock_signal_listener)

    victim.set(victim.pan)
    mock_signal_listener.assert_called_once()


def test_tool_activation_on_model_open(qtbot, victim, mock_model):
    mock_activate = MagicMock()
    victim.none.activate = mock_activate

    mock_model.opened.emit()
    mock_activate.assert_called_once()


def test_tool_deactivation_on_model_close(qtbot, victim, mock_model):
    mock_deactivate = MagicMock()
    victim.none.deactivate = mock_deactivate

    mock_model.closed.emit()
    mock_deactivate.assert_called_once()
