from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt, QMimeData, QUrl
from PySide6.QtGui import QDragEnterEvent

from suspectral.suspectral import Suspectral

import resources
assert resources


@pytest.fixture
def victim(qtbot):
    window = Suspectral()
    qtbot.addWidget(window)
    return window


def test_model_signals_update_window_title(qtbot, victim):
    fake_hypercube = MagicMock()
    fake_hypercube.name = "TestCube"

    assert victim.windowTitle() == "Suspectral"
    victim._handle_hypercube_opened(fake_hypercube)
    assert victim.windowTitle() == "Suspectral - TestCube"

    victim._handle_hypercube_closed()
    assert victim.windowTitle() == "Suspectral"


def test_handle_open_calls_model_open(qtbot, victim):
    with patch("suspectral.suspectral.QFileDialog.getOpenFileName", return_value=("path.hdr", None)):
        victim._model.open = MagicMock()
        victim._handle_open()
        victim._model.open.assert_called_once_with("path.hdr")


def test_handle_close_calls_model_close(qtbot, victim):
    victim._model.close = MagicMock()
    victim._handle_close()
    victim._model.close.assert_called_once()


def test_about_exec_called(qtbot, victim):
    with patch("suspectral.suspectral.AboutDialog.exec") as mock:
        victim._handle_about()
        mock.assert_called_once()


def test_help_exec_called(qtbot, victim):
    with patch("suspectral.suspectral.HelpDialog.exec") as mock:
        victim._handle_help()
        mock.assert_called_once()


def test_license_exec_called(qtbot, victim):
    with patch("suspectral.suspectral.LicenseDialog.exec") as mock:
        victim._handle_license()
        mock.assert_called_once()


def test_drag_enter_accepts_hdr_files(qtbot, victim):
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("file.hdr")])
    event = QDragEnterEvent(
        victim.rect().center(),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    Suspectral._handle_drag_enter(event)
    assert event.isAccepted()


def test_drag_enter_rejects_other_files(qtbot, victim):
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("file.txt")])
    event = QDragEnterEvent(
        victim.rect().center(),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    Suspectral._handle_drag_enter(event)
    assert not event.isAccepted()


def test_drag_move_accepts(qtbot, victim):
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("file.hdr")])
    event = QDragEnterEvent(
        victim.rect().center(),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    Suspectral._handle_drag_move(event)
    assert event.isAccepted()


def test_drop_opens_model(qtbot, victim):
    victim._model.open = MagicMock()
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("file.hdr")])
    event = QDragEnterEvent(
        victim.rect().center(),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    victim._handle_drop(event)
    victim._model.open.assert_called_once_with("file.hdr")
