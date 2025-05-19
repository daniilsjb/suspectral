import numpy as np
import pytest
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMenu

from suspectral.controller.image_controller import ImageController


@pytest.fixture
def mock_model(mocker):
    model = mocker.Mock()
    model.hypercube.name = "test_cube"
    return model


@pytest.fixture
def mock_image_display_view(mocker):
    image = mocker.Mock()
    pixmap = mocker.Mock(spec=QPixmap)
    image.pixmap.return_value = pixmap
    view = mocker.Mock(image=image)
    return view


@pytest.fixture
def mock_image_options_view(mocker):
    return mocker.Mock()


@pytest.fixture
def victim(qtbot, mock_model, mock_image_display_view, mock_image_options_view):
    return ImageController(
        model=mock_model,
        image_display_view=mock_image_display_view,
        image_options_view=mock_image_options_view
    )


def test_handle_hypercube_opened(victim, mock_image_display_view, mock_image_options_view):
    victim._handle_hypercube_opened()
    mock_image_display_view.reset.assert_called_once()
    mock_image_options_view.activate.assert_called_once()


def test_handle_hypercube_closed(victim, mock_image_display_view, mock_image_options_view):
    victim._handle_hypercube_closed()
    mock_image_options_view.deactivate.assert_called_once()
    mock_image_display_view.reset.assert_called_once()


def test_handle_image_changed(victim, mock_image_display_view, mocker):
    data = np.ones((10, 20, 3), dtype=np.float32)
    mocker.patch("suspectral.controller.image_controller.QPixmap.fromImage")

    victim._handle_image_changed(data)
    mock_image_display_view.display.assert_called_once()


def test_handle_context_menu(victim):
    menu = QMenu()
    victim._handle_context_menu(menu)

    actions = [action.text() for action in menu.actions()]
    assert "Copy Image" in actions
    assert "Save Image As..." in actions


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
