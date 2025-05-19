import pytest

from suspectral.view.image.image_options_view import ImageOptionsView


@pytest.fixture
def mock_model(mocker):
    return mocker.Mock()


@pytest.fixture
def victim(qtbot, mock_model):
    view = ImageOptionsView(mock_model)
    qtbot.addWidget(view)
    return view


def test_initial_state(victim):
    assert victim.currentWidget() == victim._placeholder
    assert not victim._active
    assert victim._mode_dropdown.count() == 4


def test_activate_sets_controls_visible(victim):
    victim.activate()
    assert victim._active
    assert victim.currentWidget() == victim._controls
    assert victim._mode_dropdown.currentIndex() == 0
    assert victim._mode_controls.currentWidget() == victim._modes[0]


def test_deactivate_restores_placeholder(victim):
    victim.activate()
    victim.deactivate()
    assert not victim._active
    assert victim.currentWidget() == victim._placeholder


def test_mode_switch_updates_control_stack(victim, qtbot):
    victim.activate()

    victim._mode_dropdown.setCurrentIndex(1)
    assert victim._mode_controls.currentWidget() == victim._modes[1]

    victim._mode_dropdown.setCurrentIndex(3)
    assert victim._mode_controls.currentWidget() == victim._modes[3]


def test_image_changed_signal_emitted(victim, qtbot):
    victim.activate()

    received = []
    def on_image_changed(data):
        received.append(data)

    victim.imagedChanged.connect(on_image_changed)

    dummy_data = object()
    victim._modes[0].imageChanged.emit(dummy_data)

    assert received and received[0] == dummy_data


def test_mode_status_change_disables_dropdown_item(victim, qtbot):
    victim.activate()
    model = victim._mode_dropdown.model()

    mode = victim._modes[1]
    mode.statusChanged.emit(False)

    item_enabled = model.item(1).isEnabled()
    assert not item_enabled

    mode.statusChanged.emit(True)
    assert model.item(1).isEnabled()
