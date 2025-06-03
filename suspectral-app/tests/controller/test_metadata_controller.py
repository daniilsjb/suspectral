from unittest.mock import MagicMock

import pytest

from suspectral.controller.metadata_controller import MetadataController
from suspectral.model.hypercube import Hypercube
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.metadata.metadata_view import MetadataView


@pytest.fixture
def mock_view():
    return MagicMock(spec=MetadataView)


@pytest.fixture
def mock_model():
    return HypercubeContainer()


@pytest.fixture
def victim(mock_view, mock_model, qtbot):
    return MetadataController(view=mock_view, model=mock_model)


@pytest.fixture
def mock_hypercube():
    hypercube = MagicMock(spec=Hypercube)
    hypercube.metadata = {"key": "value"}
    return hypercube


def test_handle_hypercube_opened_sets_metadata(victim, mock_view, mock_model, mock_hypercube, qtbot):
    mock_model.opened.emit(mock_hypercube)
    mock_view.set.assert_called_once_with(mock_hypercube.metadata)


def test_handle_hypercube_opened_sets_empty_metadata(victim, mock_view, mock_model, mock_hypercube, qtbot):
    mock_hypercube.metadata = {}
    mock_model.opened.emit(mock_hypercube)
    mock_view.set.assert_called_once_with({})


def test_handle_hypercube_opened_none_metadata(victim, mock_view, mock_model, mock_hypercube, qtbot):
    mock_hypercube.metadata = None
    mock_model.opened.emit(mock_hypercube)
    mock_view.set.assert_called_once_with(None)


def test_handle_hypercube_closed_clears_view(victim, mock_view, mock_model, qtbot):
    mock_model.closed.emit()
    mock_view.clear.assert_called_once()


def test_multiple_opened_signals(victim, mock_view, mock_model, qtbot, mock_hypercube):
    for _ in range(3):
        mock_model.opened.emit(mock_hypercube)

    assert mock_view.set.call_count == 3
    mock_view.set.assert_called_with(mock_hypercube.metadata)


def test_opened_and_closed_sequence(victim, mock_view, mock_model, qtbot, mock_hypercube):
    mock_model.opened.emit(mock_hypercube)
    mock_model.closed.emit()
    mock_view.set.assert_called_once_with(mock_hypercube.metadata)
    mock_view.clear.assert_called_once()


def test_opened_closed_opened_sequence(victim, mock_view, mock_model, qtbot, mock_hypercube):
    mock_model.opened.emit(mock_hypercube)
    mock_model.closed.emit()
    mock_model.opened.emit(mock_hypercube)
    assert mock_view.set.call_count == 2
    mock_view.clear.assert_called_once()


def test_boundary_empty_metadata(victim, mock_view, mock_model, mock_hypercube, qtbot):
    mock_hypercube.metadata = {}
    mock_model.opened.emit(mock_hypercube)
    mock_view.set.assert_called_once_with({})
