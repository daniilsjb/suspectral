from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QObject, Signal

from suspectral.exporter.exporter import Exporter
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.manager import ToolManager
from suspectral.tool.tool_area import AreaTool
from suspectral.tool.tool_drag import DragTool
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
    return MagicMock(ImageView)

@pytest.fixture
def mock_exporters():
    return [MagicMock(Exporter)]


def test_tool_manager_initialization(qtbot, mock_model, mock_view, mock_exporters):
    victim = ToolManager(view=mock_view, model=mock_model, exporters=mock_exporters)

    assert isinstance(victim.none, NoneTool)
    assert isinstance(victim.drag, DragTool)
    assert isinstance(victim.zoom, ZoomTool)
    assert isinstance(victim.area, AreaTool)
    assert isinstance(victim.inspect, InspectTool)

    assert victim._active_tool == victim.none


def test_set_tool_switching(qtbot, mock_model, mock_view, mock_exporters):
    victim = ToolManager(view=mock_view, model=mock_model, exporters=mock_exporters)

    mock_none_activate = MagicMock()
    mock_none_deactivate = MagicMock()
    mock_drag_activate = MagicMock()
    mock_drag_deactivate = MagicMock()

    victim.none.activate = mock_none_activate
    victim.none.deactivate = mock_none_deactivate
    victim.drag.activate = mock_drag_activate
    victim.drag.deactivate = mock_drag_deactivate

    victim.set(victim.drag)

    assert victim._active_tool == victim.drag

    mock_none_deactivate.assert_called_once()
    mock_drag_activate.assert_called_once()


def test_tool_changed_signal_emission(qtbot, mock_model, mock_view, mock_exporters):
    victim = ToolManager(view=mock_view, model=mock_model, exporters=mock_exporters)

    mock_signal_listener = MagicMock()
    victim.toolChanged.connect(mock_signal_listener)

    victim.set(victim.drag)

    mock_signal_listener.assert_called_once()


def test_tool_activation_on_model_open(qtbot, mock_model, mock_view, mock_exporters):
    victim = ToolManager(view=mock_view, model=mock_model, exporters=mock_exporters)

    mock_activate = MagicMock()
    victim.none.activate = mock_activate

    mock_model.opened.emit()

    mock_activate.assert_called_once()


def test_tool_deactivation_on_model_close(qtbot, mock_model, mock_view, mock_exporters):
    victim = ToolManager(view=mock_view, model=mock_model, exporters=mock_exporters)

    mock_deactivate = MagicMock()
    victim.none.deactivate = mock_deactivate

    mock_model.closed.emit()

    mock_deactivate.assert_called_once()
