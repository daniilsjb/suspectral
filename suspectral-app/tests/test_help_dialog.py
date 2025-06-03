import pytest
from PySide6.QtWidgets import QTextBrowser, QDialogButtonBox

from suspectral.help import HelpDialog


@pytest.fixture
def victim(qtbot):
    victim = HelpDialog()
    qtbot.addWidget(victim)
    return victim


def test_help_dialog(victim):
    assert victim.windowTitle() == "Help"

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
