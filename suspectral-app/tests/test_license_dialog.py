import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextEdit, QDialogButtonBox

from suspectral.license import LicenseDialog


@pytest.fixture
def victim(qtbot):
    victim = LicenseDialog()
    qtbot.addWidget(victim)
    return victim


def test_dialog_properties(victim):
    assert victim.windowTitle() == "License Agreement"
    assert victim.width() == 500
    assert victim.height() == 400


def test_license_text_is_set_correctly(victim):
    layout = victim.layout()
    assert layout.count() == 2

    editor = layout.itemAt(0).widget()
    assert isinstance(editor, QTextEdit)

    text = editor.toPlainText()
    assert "MIT License" in text
    assert "Copyright" in text


def test_text_edit_is_read_only(victim):
    text_edit = victim.layout().itemAt(0).widget()
    assert text_edit.isReadOnly()


def test_ok_button_triggers_accept(victim, qtbot):
    victim.show()
    ok_button = victim.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)

    with qtbot.waitSignal(victim.accepted, timeout=500):
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
