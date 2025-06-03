import builtins
import pytest
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QStandardPaths
from suspectral.exporter.writer_file import FileWriter


@pytest.mark.parametrize("mode,data", [
    ("w", "textual content"),
    ("wb", b"\xDE\xAD\xBE\xEF"),
])
def test_file_writer_saves_to_disk(mocker, mode, data):
    victim = FileWriter(suffix=".npy", filters="NumPy (*.npy)")
    mocker.patch.object(QFileDialog, "getSaveFileName", return_value=("/fake/path/file.npy", None))
    mocker.patch.object(QStandardPaths, "writableLocation", return_value="/fake/downloads")

    mock_open = mocker.mock_open()
    mocker.patch.object(builtins, "open", mock_open)

    victim.write("filename_base", data)

    mock_open.assert_called_once_with("/fake/path/file.npy", mode)
    mock_open().write.assert_called_once_with(data)


def test_file_writer_cancelled_does_nothing(mocker):
    victim = FileWriter(suffix=".txt", filters="Text Files (*.txt)")
    mocker.patch.object(QFileDialog, "getSaveFileName", return_value=("", None))
    mocker.patch.object(QStandardPaths, "writableLocation", return_value="/downloads")

    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    victim.write("name", "irrelevant")

    mock_open.assert_not_called()
