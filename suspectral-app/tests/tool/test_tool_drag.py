import pytest
from PySide6.QtWidgets import QGraphicsView

from suspectral.tool.tool_drag import DragTool
from suspectral.view.image.image_view import ImageView


@pytest.fixture
def image_view(qtbot):
    image_view = ImageView()
    qtbot.addWidget(image_view)
    return image_view

@pytest.fixture
def set_drag_mode(mocker, image_view):
    return mocker.patch.object(image_view, "setDragMode")


def test_drag_tool_activation(qtbot, image_view, set_drag_mode):
    drag_tool = DragTool(image_view)
    drag_tool.activate()

    image_view.show()
    qtbot.waitExposed(image_view)

    set_drag_mode.assert_called_once_with(QGraphicsView.DragMode.ScrollHandDrag)


def test_drag_tool_deactivation(qtbot, image_view, set_drag_mode):
    drag_tool = DragTool(image_view)
    drag_tool.deactivate()

    image_view.show()
    qtbot.waitExposed(image_view)

    set_drag_mode.assert_called_once_with(QGraphicsView.DragMode.NoDrag)
