import pytest
from PySide6.QtWidgets import QTextEdit

from suspectral.license import LicenseDialog


@pytest.fixture
def victim(qtbot):
    victim = LicenseDialog()
    qtbot.addWidget(victim)
    return victim


def test_license_dialog(victim):
    assert victim.windowTitle() == "License Agreement"

    layout = victim.layout()
    assert layout.count() == 2

    editor = layout.itemAt(0).widget()
    assert isinstance(editor, QTextEdit)
    assert editor.isReadOnly()

    text = editor.toPlainText()
    assert "MIT License" in text
    assert "Copyright" in text
    assert "2025" in text
