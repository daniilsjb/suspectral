from unittest.mock import MagicMock

import numpy as np
import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMenu

from suspectral.controller.image_controller import ImageController
from suspectral.tool.manager import ToolManager


@pytest.fixture
def mock_model():
    model = MagicMock()
    model.hypercube.name = "test_cube"
    return model


@pytest.fixture
def mock_image_display_view():
    pixmap = MagicMock(spec=QPixmap)
    image = MagicMock()
    image.pixmap.return_value = pixmap
    return MagicMock(image=image)


@pytest.fixture
def mock_tools():
    return MagicMock(spec=ToolManager)


@pytest.fixture
def mock_image_options_view():
    return MagicMock()


@pytest.fixture
def victim(mock_model, mock_tools, mock_image_display_view, mock_image_options_view):
    return ImageController(
        model=mock_model,
        tools=mock_tools,
        image_display_view=mock_image_display_view,
        image_controls_view=mock_image_options_view
    )


def test_handle_hypercube_opened(victim, mock_image_display_view, mock_image_options_view):
    victim._handle_hypercube_opened()
    mock_image_display_view.reset.assert_called_once()
    mock_image_options_view.activate.assert_called_once()


def test_handle_hypercube_closed(victim, mock_image_display_view, mock_image_options_view):
    victim._handle_hypercube_closed()
    mock_image_display_view.reset.assert_called_once()
    mock_image_options_view.deactivate.assert_called_once()


def test_handle_image_changed(victim, mock_image_display_view, mocker):
    data = np.ones((10, 20, 3), dtype=np.float32)
    mocker.patch("suspectral.controller.image_controller.QPixmap.fromImage")

    victim._handle_image_changed(data)
    mock_image_display_view.display.assert_called_once()


def test_copy_image(victim, mocker, mock_image_display_view):
    clipboard_mock = mocker.Mock()
    mocker.patch("suspectral.controller.image_controller.QApplication.clipboard", return_value=clipboard_mock)

    victim.copy_image()
    clipboard_mock.setPixmap.assert_called_once_with(mock_image_display_view.image.pixmap())


def test_save_image_success(victim, mocker, mock_model, mock_image_display_view):
    mock_pixmap = mock_image_display_view.image.pixmap()
    mock_pixmap.save.return_value = True

    mocker.patch("suspectral.controller.image_controller.QStandardPaths.writableLocation", return_value="/downloads")
    mocker.patch("suspectral.controller.image_controller.QFileDialog.getSaveFileName",
                 return_value=("/downloads/test.png", None))

    victim.save_image()
    mock_pixmap.save.assert_called_once_with("/downloads/test.png")


def test_save_image_failure(victim, mocker, mock_image_display_view):
    mock_pixmap = mock_image_display_view.image.pixmap()
    mock_pixmap.save.return_value = False

    mocker.patch("suspectral.controller.image_controller.QStandardPaths.writableLocation", return_value="/downloads")
    mocker.patch("suspectral.controller.image_controller.QFileDialog.getSaveFileName",
                 return_value=("/downloads/test.png", None))

    critical_mock = mocker.patch("suspectral.controller.image_controller.QMessageBox.critical")
    victim.save_image()
    critical_mock.assert_called_once()


def test_handle_tool_changed_clears_reference_points(victim, mock_image_options_view):
    victim._handle_tool_changed()
    mock_image_options_view.clear_reference_points.assert_called_once()


def test_handle_selection_changed_clears_reference_points(victim, mock_image_options_view):
    victim._handle_selection_changed()
    mock_image_options_view.clear_reference_points.assert_called_once()


def test_handle_selection_sampled_adds_reference_points(victim, mock_image_options_view):
    xs = np.array([1, 2])
    ys = np.array([10, 20])

    victim._handle_selection_sampled(xs, ys)

    expected_points = [QPoint(x, y) for y in ys for x in xs]
    calls = [call.args[0] for call in mock_image_options_view.add_reference_points.call_args_list]

    assert calls == expected_points


def test_handle_pixel_clicked_adds_reference_point(victim, mock_image_options_view):
    point = QPoint(5, 5)
    victim._handle_pixel_clicked(point)
    mock_image_options_view.add_reference_points.assert_called_once_with(point)


def test_handle_pixel_cleared_clears_reference_points(victim, mock_image_options_view):
    victim._handle_pixel_cleared()
    mock_image_options_view.clear_reference_points.assert_called_once()


def test_menu_context(qtbot, victim):
    menu = QMenu()
    victim._handle_context_menu(menu)
    labels = [action.text() for action in menu.actions() if not action.isSeparator()]
    assert labels == ["Copy Image", "Save Image As..."]
