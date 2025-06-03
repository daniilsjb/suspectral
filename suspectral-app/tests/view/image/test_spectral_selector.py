from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PySide6.QtCore import QMimeData, QUrl, Qt, QEvent, QResource, QPoint
from PySide6.QtGui import QDropEvent, QDragEnterEvent
from PySide6.QtWidgets import QMessageBox

from suspectral.view.image.spectral_selector import SpectralSelector


@pytest.fixture
def victim(qtbot):
    widget = SpectralSelector(columns=["Wavelength", "Reflectance"])
    qtbot.addWidget(widget)
    return widget


def test_clear_emits_signal(qtbot, victim):
    with qtbot.waitSignal(victim.valueCleared):
        victim.clear()

    assert victim.name_ is None
    assert victim.data_ is None
    assert not victim._preview.text()


def test_use_valid_file(tmp_path, qtbot, victim):
    file = tmp_path / "spectrum.csv"
    file.write_text("Wavelength,Reflectance\n500,0.5\n600,0.6")

    with qtbot.waitSignal(victim.valueChanged) as signal:
        victim._use_file(str(file))

    assert signal.args == [str(file)]
    assert victim.name_ == str(file)
    assert victim._preview.text() == "spectrum.csv"

    assert np.array_equal(victim.data_["Wavelength"], np.array([500, 600]))
    assert np.array_equal(victim.data_["Reflectance"], np.array([0.5, 0.6]))


def test_use_file_invalid_data_type(tmp_path, qtbot, victim):
    file = tmp_path / "bad.csv"
    file.write_text("Wavelength,Reflectance\nA,B")

    with patch.object(QMessageBox, "critical") as mock_critical:
        victim._use_file(str(file))
        mock_critical.assert_called_once()
        assert victim.name_ is None


def test_use_file_invalid_data_shape(tmp_path, qtbot, victim):
    file = tmp_path / "bad.csv"
    file.write_text("Wavelength,Reflectance\nA,B,C")

    with patch.object(QMessageBox, "critical") as mock_critical:
        victim._use_file(str(file))
        mock_critical.assert_called_once()
        assert victim.name_ is None


def test_use_file_invalid_columns(tmp_path, qtbot, victim):
    file = tmp_path / "wrong.csv"
    file.write_text("A,B,C\n1,2,3")

    with patch.object(QMessageBox, "critical") as mock_critical:
        victim._use_file(str(file))
        mock_critical.assert_called_once()
        assert victim.name_ is None


def test_use_preset(qtbot):
    resource_data = b"Wavelength,Reflectance\n400,0.1\n500,0.2"

    with patch.object(QResource, "data", return_value=resource_data):
        victim = SpectralSelector(
            columns=["Wavelength", "Reflectance"],
            presets=[("Foo", ":/fake/path.csv")],
        )

        qtbot.addWidget(victim)
        with qtbot.waitSignal(victim.valueChanged) as signal:
            victim._use_preset("Foo", ":/fake/path.csv")

        assert signal.args == ["Foo"]
        assert victim.name_ == "Foo"
        assert victim._preview.text() == "Foo"

        assert np.array_equal(victim.data_["Wavelength"], np.array([400, 500]))
        assert np.array_equal(victim.data_["Reflectance"], np.array([0.1, 0.2]))


def test_drag_enter_accepts_csv(qtbot, victim):
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile("/some/file.csv")])
    event = QDragEnterEvent(
        QPoint(0, 0),
        Qt.DropAction.CopyAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    result = victim._handle_drag_enter(event)
    assert result is True
    assert event.isAccepted()


def test_drop_event_uses_file_mocked(qtbot, victim):
    fake_path = "/some/fake/path.csv"

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(fake_path)])
    event = QDragEnterEvent(
        QPoint(0, 0),
        Qt.DropAction.CopyAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    with patch.object(victim, "_use_file") as mock_use_file:
        victim._handle_drop_event(event)

    mock_use_file.assert_called_once_with(fake_path)


def test_event_filter_for_drag_and_drop(qtbot, victim):
    drop_event = MagicMock(spec=QDropEvent)
    drag_event = MagicMock(spec=QDragEnterEvent)
    drop_event.mimeData().hasUrls.return_value = True
    drag_event.mimeData().hasUrls.return_value = True

    drop_event.mimeData().urls.return_value = [QUrl.fromLocalFile("valid.csv")]
    drag_event.mimeData().urls.return_value = [QUrl.fromLocalFile("valid.csv")]

    drag_event.type.return_value = QEvent.Type.DragEnter
    victim.eventFilter(victim._preview, drag_event)

    drop_event.type.return_value = QEvent.Type.Drop
    with patch.object(victim, "_use_file") as mock_use_file:
        victim.eventFilter(victim._preview, drop_event)
        mock_use_file.assert_called_once()


@patch("suspectral.view.image.spectral_selector.QFileDialog.getOpenFileName", return_value=("/mock/path.csv", ""))
def test_browse_with_file_selected(qtbot, victim):
    with patch.object(victim, "_use_file") as mock_use_file:
        victim._browse()
        mock_use_file.assert_called_once_with("/mock/path.csv")


@patch("suspectral.view.image.spectral_selector.QFileDialog.getOpenFileName", return_value=("", ""))
def test_browse_without_file_selected(qtbot, victim):
    with patch.object(victim, "_use_file") as mock_use_file:
        victim._browse()
        mock_use_file.assert_not_called()


def test_menu_contents(qtbot):
    presets = [("Foo", ":/foo.csv"), ("Bar", ":/bar.csv")]
    victim = SpectralSelector(columns=["Wavelength", "Reflectance"], presets=presets)
    qtbot.addWidget(victim)

    with patch("suspectral.view.image.spectral_selector.QMenu") as mock_menu_class:
        mock_menu = MagicMock()
        mock_menu_class.return_value = mock_menu

        victim._show_menu()

        added_labels = [call_args[0][0] for call_args in mock_menu.addAction.call_args_list]
        assert added_labels == [
            "Preset: Foo",
            "Preset: Bar",
            "Custom (CSV)",
            "Remove",
        ]
