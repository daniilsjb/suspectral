import pytest
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QLabel, QDialogButtonBox

from suspectral.about import AboutDialog

import resources
assert resources


@pytest.fixture
def victim(qtbot):
    QCoreApplication.setApplicationVersion("1.2.3")
    victim = AboutDialog()
    qtbot.addWidget(victim)
    return victim


def test_dialog_properties(victim):
    assert victim.windowTitle() == "About"
    assert victim.width() == 300
    assert victim.height() == 200


def test_dialog_layout_and_widgets(victim):
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

    expected_text = (
        "<strong>Suspectral</strong>"
        "<p>Copyright &copy; 2025 Daniils Buts</p>"
        "<p>Software for visualization and analysis of hyperspectral imaging data.</p>"
        f"<p>Version 1.2.3</p>"
    )
    assert text_label.text() == expected_text

    buttons = layout.itemAt(2).widget()
    assert isinstance(buttons, QDialogButtonBox)
    assert buttons.button(QDialogButtonBox.StandardButton.Ok) is not None


def test_dialog_accepts_on_ok_click(victim, qtbot):
    victim.show()
    ok_button = victim.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)

    with qtbot.waitSignal(victim.accepted, timeout=500):
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
