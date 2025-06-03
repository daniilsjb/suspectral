from unittest.mock import MagicMock

import numpy as np
import pytest
from PySide6.QtCore import QPoint

from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.view.image.spectral_reference import SpectralReference


@pytest.fixture
def mock_model():
    model = MagicMock(spec=HypercubeContainer)
    model.hypercube.read_pixel.return_value = np.array([0.1, 0.2, 0.3])
    return model


@pytest.fixture
def victim(qtbot, mock_model):
    victim = SpectralReference(model=mock_model)
    qtbot.addWidget(victim)
    return victim


def test_initial_state(victim):
    assert victim._select.count() == 1
    assert victim._select.itemText(0) == "Select..."
    assert victim._points == []


def test_add_point_updates_dropdown(victim):
    victim.add(QPoint(3, 5))
    assert len(victim._points) == 1
    assert victim._points[0] == QPoint(3, 5)
    assert victim._select.count() == 2
    assert victim._select.itemText(1) == "Selection (1)"


def test_clear_resets_state(victim):
    victim.add(QPoint(1, 1))
    victim.add(QPoint(2, 2))
    assert victim._select.count() == 3
    assert len(victim._points) == 2

    victim.clear()

    assert victim._select.count() == 1
    assert victim._select.itemText(0) == "Select..."
    assert victim._points == []


def test_get_returns_correct_spectrum(victim, mock_model):
    victim.add(QPoint(2, 3))
    victim.add(QPoint(4, 5))

    victim._select.setCurrentIndex(2)
    spectrum = victim.get()

    expected = mock_model.hypercube.read_pixel(5, 4)
    assert np.allclose(spectrum, expected)


def test_get_returns_none_if_not_selected(victim):
    victim.add(QPoint(2, 3))
    victim._select.setCurrentIndex(0)
    assert victim.get() is None
