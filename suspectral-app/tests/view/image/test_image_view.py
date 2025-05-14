from unittest.mock import patch

import pytest
from PySide6.QtCore import QPoint, QRectF, QEvent
from PySide6.QtGui import QPixmap, QMouseEvent, QWheelEvent, QContextMenuEvent, Qt
from PySide6.QtWidgets import QMenu

from suspectral.view.image.image_view import ImageView


@pytest.fixture
def victim(qtbot):
    view = ImageView()
    qtbot.addWidget(view)
    return view


def test_display_and_scene_rect(victim):
    pixmap = QPixmap(20, 30)
    victim.display(pixmap)
    assert victim.image.pixmap().size().width() == 20
    assert victim.image.pixmap().size().height() == 30
    assert victim.sceneRect() == QRectF(0, 0, 20, 30)


def test_reset(victim):
    pixmap = QPixmap(5, 5)
    victim.display(pixmap)
    victim.reset()
    assert victim.image.pixmap().isNull()
    assert victim.sceneRect() == QRectF(0, 0, 1, 1)
    assert victim.transform().isIdentity()
    assert victim._zoom == 1.0


@pytest.mark.parametrize("method,angle", [
    ("rotate_left", -90.0),
    ("rotate_right", +90.0),
])
def test_rotate_methods_call_rotate(victim, method, angle):
    with patch.object(victim, "rotate") as spy:
        getattr(victim, method)()
    spy.assert_called_once_with(angle)


@pytest.mark.parametrize("method,sx,sy", [
    ("flip_vertically", +1.0, -1.0),
    ("flip_horizontally", -1.0, +1.0),
])
def test_flip_methods_call_scale(victim, method, sx, sy):
    with patch.object(victim, "scale") as spy:
        getattr(victim, method)()
    spy.assert_called_once_with(sx, sy)


@pytest.mark.parametrize("start,factor,expected", [
    (1.0, 1.2, 1.2),
    (0.5, 0.1, ImageView.ZOOM_MIN),
    (50.0, 10.0, ImageView.ZOOM_MAX),
])
def test_zoom_boundaries(victim, start, factor, expected):
    victim._zoom = start
    with patch.object(victim, "scale") as spy:
        victim.zoom(factor)
    scale_args = spy.call_args[0]
    assert pytest.approx(scale_args[0]) == expected / start
    assert victim._zoom == expected


def test_zoom_in_out_aliases(victim):
    with patch.object(victim, "zoom") as spy:
        victim.zoom_in(2.0)
    spy.assert_called_with(2.0)
    with patch.object(victim, "zoom") as spy2:
        victim.zoom_out(3.0)
    spy2.assert_called_with(1.0 / 3.0)


def test_zoom_fit_sets_zoom(victim):
    fake_transform = type("T", (), {"m11": lambda self: 2.5, "m12": lambda self: 0, "m21": lambda self: 0,
                                    "m22": lambda self: 0})()
    victim.fitInView = lambda *args, **kwargs: None
    victim.transform = lambda: fake_transform
    victim.zoom_fit()
    assert victim._zoom == 2.5


def make_wheel_event(delta):
    p = QPoint(5, 5)
    return QWheelEvent(p, p, QPoint(0, 0), QPoint(0, delta), Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate, False)


def test_wheel_event_calls_zoom_in_out(victim):
    with patch.object(victim, "zoom_in") as spy_in:
        victim.wheelEvent(make_wheel_event(120))
    spy_in.assert_called_once()
    with patch.object(victim, "zoom_out") as spy_out:
        victim.wheelEvent(make_wheel_event(-120))
    spy_out.assert_called_once()


# def test_mouse_move_inside_and_outside(qtbot, victim):
#     victim.show()
#     pix = QPixmap(100, 100)
#     victim.display(pix)
#     # inside move
#     with qtbot.waitSignal(victim.cursorMovedInside) as sig_in:
#         qtbot.mouseMove(victim.viewport(), QPoint(10, 10))
#     assert sig_in.args[0] == QPoint(10, 10)
#     # outside move
#     with qtbot.waitSignal(victim.cursorMovedOutside):
#         qtbot.mouseMove(victim.viewport(), QPoint(200, 200))
#
# def test_context_menu_event(qtbot, victim):
#     victim.show()
#     # before image: right‐click should not emit
#     with pytest.raises(qtbot.TimeoutError):
#         with qtbot.waitSignal(victim.contextMenuRequested, timeout=100):
#             qtbot.mouseClick(victim.viewport(), Qt.RightButton, pos=QPoint(5,5))
#     # after display, right‐click should emit and exec
#     victim.display(QPixmap(10, 10))
#     def fake_exec(self, pos): self._executed = True
#     with patch.object(QMenu, "exec", fake_exec):
#         with qtbot.waitSignal(victim.contextMenuRequested) as sig:
#             qtbot.mouseClick(victim.viewport(), Qt.RightButton, pos=QPoint(5,5))
#     menu = sig.args[0]
#     assert isinstance(menu, QMenu)
#     assert getattr(menu, "_executed", False)
