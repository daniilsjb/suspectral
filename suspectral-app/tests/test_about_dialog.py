from unittest.mock import patch

import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QLabel, QDialogButtonBox

from suspectral.about import AboutDialog

import resources
assert resources


@pytest.fixture
def victim(qtbot):
    with patch.object(QtCore.QCoreApplication, "applicationVersion", return_value="1.2.3"):
        victim = AboutDialog()
        qtbot.addWidget(victim)
        return victim


def test_about_dialog(victim):
    assert victim.windowTitle() == "About"

    layout = victim.layout()
    assert layout.count() == 3

    logo = layout.itemAt(0).widget()
    assert isinstance(logo, QLabel)
    assert not logo.pixmap().isNull()
    assert logo.alignment() == logo.alignment().AlignCenter

    text_label = layout.itemAt(1).widget()
    assert isinstance(text_label, QLabel)
    assert text_label.wordWrap()
    assert text_label.alignment() == text_label.alignment().AlignCenter

    assert text_label.text() == (
        "<strong>Suspectral</strong>"
        "<p>Copyright &copy; 2025 Daniils Buts</p>"
        "<p>Software for visualization and extraction of hyperspectral imaging data.</p>"
        f"<p>Version 1.2.3</p>"
    )

    buttons = layout.itemAt(2).widget()
    assert isinstance(buttons, QDialogButtonBox)
    assert buttons.button(QDialogButtonBox.StandardButton.Ok) is not None
