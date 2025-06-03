from unittest.mock import MagicMock

import pytest

from suspectral.controller.toolbar_controller import ToolbarController
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.toolbar.toolbar_view import ToolbarView


@pytest.fixture
def mock_view():
    return MagicMock(spec=ToolbarView)


@pytest.fixture
def mock_model():
    return MagicMock(spec=HypercubeContainer)


@pytest.fixture
def victim(mock_view, mock_model):
    return ToolbarController(view=mock_view, model=mock_model)


def test_handle_hypercube_opened_enables_view(victim, mock_view):
    victim._handle_hypercube_opened()
    mock_view.setEnabled.assert_called_once_with(True)


def test_handle_hypercube_closed_disables_view(victim, mock_view):
    victim._handle_hypercube_closed()
    mock_view.setEnabled.assert_called_once_with(False)
