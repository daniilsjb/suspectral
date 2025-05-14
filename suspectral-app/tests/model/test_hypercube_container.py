from unittest.mock import patch, MagicMock

import pytest

from suspectral.model.hypercube_container import HypercubeContainer


@pytest.fixture
def mock_hypercube():
    return MagicMock()


@patch("suspectral.model.hypercube_container.Hypercube")
def test_open_emits_opened_signal(mock_hypercube_class, mock_hypercube, qtbot):
    mock_hypercube_class.return_value = mock_hypercube

    victim = HypercubeContainer()
    with qtbot.waitSignal(victim.opened, timeout=1000) as blocker:
        result = victim.open("dummy/path")

    assert victim.hypercube == mock_hypercube
    assert result == mock_hypercube
    assert blocker.args == [mock_hypercube]


@patch("suspectral.model.hypercube_container.Hypercube")
def test_close_emits_closed_signal(mock_hypercube_class, mock_hypercube, qtbot):
    mock_hypercube_class.return_value = mock_hypercube

    victim = HypercubeContainer()
    victim.open("dummy/path")

    with qtbot.waitSignal(victim.closed, timeout=1000):
        victim.close()

    assert victim.hypercube is None


@patch("suspectral.model.hypercube_container.Hypercube")
def test_open_closes_existing_first(mock_hypercube_class, mock_hypercube, qtbot):
    mock_hypercube_class.return_value = mock_hypercube

    victim = HypercubeContainer()
    victim.open("dummy/path/first")

    with qtbot.waitSignals([victim.closed, victim.opened], timeout=1000) as blockers:
        victim.open("dummy/path/second")

    assert victim.hypercube == mock_hypercube
