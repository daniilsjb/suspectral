import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextBrowser, QDialogButtonBox

from suspectral.help import HelpDialog


@pytest.fixture
def victim(qtbot):
    victim = HelpDialog()
    qtbot.addWidget(victim)
    return victim


def test_dialog_properties(victim):
    assert victim.windowTitle() == "Help"
    assert victim.minimumWidth() == 600
    assert victim.minimumHeight() == 400
    assert victim.width() == 600
    assert victim.height() == 400


def test_dialog_contains_text_browser_and_button_box(victim):
    layout = victim.layout()
    assert layout.count() == 2

    browser = layout.itemAt(0).widget()
    assert isinstance(browser, QTextBrowser)

    html = browser.toHtml()
    assert "Suspectral" in html
    assert "<table" in html

    buttons = layout.itemAt(1).widget()
    assert isinstance(buttons, QDialogButtonBox)
    assert buttons.button(QDialogButtonBox.StandardButton.Ok) is not None


def test_ok_button_closes_dialog(victim, qtbot):
    victim.show()
    ok_button = victim.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)

    with qtbot.waitSignal(victim.accepted, timeout=500):
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
