from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from suspectral.exporter.writer_clipboard import ClipboardWriter


def test_clipboard_writer(mocker):
    victim = ClipboardWriter()

    clipboard_mock = MagicMock()
    mocker.patch.object(QApplication, "clipboard", return_value=clipboard_mock)

    data = "some tab-separated values\n1\t2\t3"
    victim.write("test_name", data)

    clipboard_mock.setText.assert_called_once_with(data)
